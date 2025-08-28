#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
import sys as _sys
import contextlib as _contextlib
import json
import logging
import time
import weakref as _weakref
from collections import OrderedDict, deque
from functools import partial

import nevergrad
import numpy as np
from nevergrad.common import errors
from nevergrad.common import tools as ngtools
from nevergrad.optimization import utils
from nevergrad.parametrization import parameter as p

from .. import __version__, _distutils_loose_version, exceptions, shared
from ..gtdoe.generator import _append_field_spec, _SolutionSnapshotFactory
from ..loggers import LogLevel
from ..result import (GT_SOLUTION_TYPE_CONVERGED,
                      GT_SOLUTION_TYPE_NOT_DOMINATED, Result, solution_filter)
from ..shared import _NONE, _SHALLOW
from ..status import IN_PROGRESS, SUCCESS, UNSUPPORTED_PROBLEM, USER_TERMINATED, INVALID_PROBLEM
from ..utils import buildinfo
from ..utils.designs import (_DetachableSingleCallableRef,
                             _postprocess_designs, _SolutionSnapshot)
from . import api, diagnostic
from .problem import _get_gtopt_positive_infinity, _limited_evaluations
from .solver import ValidationResult

GTOPT_POSITIVE_INFINITY = _get_gtopt_positive_infinity()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False


class BatchOptimizer(nevergrad.optimizers.NGOpt):

  def __init__(self, *args, **kwargs):
    super(BatchOptimizer, self).__init__(*args, **kwargs)
    self._asked_batch_cache = set()

  def _tell(self, *args, **kwargs):
    super(BatchOptimizer, self).tell(*args, **kwargs)
    # The whole batch was calculated, so just clear the cache.
    self._asked_batch_cache.clear()

  def _ask(self, objective_function, constraint_violation, n_attempts):
    candidate = super(BatchOptimizer, self).ask()
    if n_attempts == 0:
      return candidate

    def _not_in_archives(candidate):
      # Check both the global Nevergrad archive and cache of the current batch points,
      # that have not been sent to the blackbox yet
      key = candidate.get_standardized_data(reference=self.parametrization)
      # Note that we can not use the key for batch cache since it may be different for the same value within a batch
      return key not in self.archive and candidate.args not in self._asked_batch_cache

    def _has_unknown_responses(candidate):
      # If any of objectives or constraints is not calculated then the point is not considered as duplicate.
      # Actually, both objectives and constraints are evaluated for each point.
      kwargs = candidate.kwargs.copy()
      kwargs["cache_only"] = True
      cached_objectives = objective_function(*candidate.args, **kwargs)
      if cached_objectives is None:
        return True
      for c_func in constraint_violation or []:
        if c_func(candidate.value, cache_only=True) is None:
          return True
      return False

    # Fast check in Nevergrad archive, then slow check for calculated responses.
    # If the point was found in the global archive, it should have all the responses calculated.
    if _not_in_archives(candidate) and _has_unknown_responses(candidate):
      self._asked_batch_cache.add(candidate.args)
      return candidate

    logger.debug("Trying to find a unique candidate instead of the known one %s" % str(candidate.args))
    for i in range(n_attempts):
      # We can not use the `ask` method since it consumes the budget, so just sample from the design space.
      new_candidate = self.parametrization.sample()
      if _not_in_archives(new_candidate) and _has_unknown_responses(new_candidate):
        logger.debug("Unique candidate was found after %d attempts: %s" % (i + 1, str(new_candidate.args)))
        # Note that if the candidate is included to the current batch, it wont have any calculated responses
        if not _has_unknown_responses(candidate):
          kwargs = candidate.kwargs.copy()
          kwargs["cache_only"] = True
          cached_objectives = objective_function(*candidate.args, **kwargs)
          if constraint_violation is not None:
            cached_constraints = [c_func(candidate.value, cache_only=True) for c_func in constraint_violation]
            self.tell(candidate, cached_objectives, cached_constraints)
          else:
            self.tell(candidate, cached_objectives)
        self._asked_batch_cache.add(new_candidate.args)
        return new_candidate
    else:
      # Failed to find a unique candidate
      logger.debug("Failed to find a unique candidate, using the proposed one %s" % str(candidate.args))
      self._asked_batch_cache.add(candidate.args)
      return candidate

  def minimize(
      self,
      objective_function,
      executor = None,
      batch_mode = False,
      verbosity = 0,
      constraint_violation = None,
      n_unique_sampling_attempts=10,
  ):
    """Optimization (minimization) procedure

    !!! This override is needed for the following reasons:  !!!
     - no support for parallel execution of constraints
     - no guarantee that asked points are unique, hence the batch size can not be guaranteed

    Parameters
    ----------
    objective_function: callable
        A callable to optimize (minimize)
    executor: Executor
        An executor object, with method :code:`submit(callable, *args, **kwargs)` and returning a Future-like object
        with methods :code:`done() -> bool` and :code:`result() -> float`. The executor role is to dispatch the execution of
        the jobs locally/on a cluster/with multithreading depending on the implementation.
        Eg: :code:`concurrent.futures.ProcessPoolExecutor`
    batch_mode: bool
        when :code:`num_workers = n > 1`, whether jobs are executed by batch (:code:`n` function evaluations are launched,
        we wait for all results and relaunch n evals) or not (whenever an evaluation is finished, we launch
        another one)
    verbosity: int
        print information about the optimization (0: None, 1: fitness values, 2: fitness values and recommendation)
    constraint_violation: list of functions or None
        each function in the list returns >0 for a violated constraint.

    Returns
    -------
    ng.p.Parameter
        The candidate with minimal value. :code:`ng.p.Parameters` have field :code:`args` and :code:`kwargs` which can
        be directly used on the function (:code:`objective_function(*candidate.args, **candidate.kwargs)`).

    Note
    ----
    for evaluation purpose and with the current implementation, it is better to use batch_mode=True
    """
    # pylint: disable=too-many-branches
    if self.budget is None:
      raise ValueError("Budget must be specified")
    if executor is None:
      executor = utils.SequentialExecutor()  # defaults to run everything locally and sequentially
      if self.num_workers > 1:
        self._warn(
          "num_workers = %d > 1 is suboptimal when run sequentially" % self.num_workers,
          errors.InefficientSettingsWarning,
        )
    assert executor is not None
    tmp_runnings = []
    tmp_finished = deque()
    # go
    sleeper = ngtools.Sleeper()  # manages waiting time depending on execution time of the jobs
    remaining_budget = self.budget - self.num_ask
    first_iteration = True
    #
    while remaining_budget or self._running_jobs or self._finished_jobs:
      # # # # # Update optimizer with finished jobs # # # # #
      # this is the first thing to do when resuming an existing optimization run
      # process finished
      if self._finished_jobs:
        if (remaining_budget or sleeper._start is not None) and not first_iteration:
          # ignore stop if no more suggestion is sent
          # this is an ugly hack to avoid warnings at the end of steady mode
          sleeper.stop_timer()

        violation_results = None
        if constraint_violation is not None:
          violation_results = []
          for constraint_function in constraint_violation:
            constraint_jobs = []
            for candidate, job in self._finished_jobs:
              constraint_jobs.append(
                (candidate, executor.submit(constraint_function, candidate.value))
              )
            while any(not job[1].done() for job in constraint_jobs):
              sleeper.sleep()
            violation_results.append([job[1].result() for job in constraint_jobs])
          # Transpose so that the rows correspond to evaluated points
          violation_results = list(zip(*violation_results))

        while self._finished_jobs:
          x, job = self._finished_jobs[0]
          result = job.result()
          if constraint_violation is not None:
            violation = violation_results.pop(0)
            self._tell(x, result, violation)
          else:
            self._tell(x, result)
          self._finished_jobs.popleft()  # remove it after the tell to make sure it was indeed "told" (in case of interruption)
          if verbosity:
            logger.info("Updating fitness with value %s" % str(result))
        if verbosity:
          logger.info("%d remaining budget and %d running jobs" % (remaining_budget, len(self._running_jobs)))
          if verbosity > 1:
            logger.info("Current pessimistic best is: %s" % str(self.current_bests["pessimistic"]))
      elif not first_iteration:
        sleeper.sleep()
      # # # # # Start new jobs # # # # #
      if not batch_mode or not self._running_jobs:
        n_points_to_ask = max(0, min(remaining_budget, self.num_workers - len(self._running_jobs)))
        if verbosity and n_points_to_ask:
          logger.info("Launching %d jobs with new suggestions" % n_points_to_ask)
        for _ in range(n_points_to_ask):
          try:
            # Try to ensure the proper batch size by removing the duplicate points
            candidate = self._ask(objective_function, constraint_violation, n_unique_sampling_attempts)
          except errors.NevergradEarlyStopping:
            remaining_budget = 0
            break
          self._running_jobs.append(
            (candidate, executor.submit(objective_function, *candidate.args, **candidate.kwargs))
          )
        if n_points_to_ask:
          sleeper.start_timer()
      if remaining_budget > 0:  # early stopping sets it to 0
        remaining_budget = self.budget - self.num_ask
      # split (repopulate finished and runnings in only one loop to avoid
      # weird effects if job finishes in between two list comprehensions)
      tmp_runnings, tmp_finished = [], deque()
      for x_job in self._running_jobs:
        (tmp_finished if x_job[1].done() else tmp_runnings).append(x_job)
      self._running_jobs, self._finished_jobs = tmp_runnings, tmp_finished
      first_iteration = False
    return self.provide_recommendation() if self.num_objectives == 1 else p.Constant(None)


class _BatchFuture(object):
  def __init__(self, args, kwargs, callback_on_check=None):
    self._args = args
    self._kwargs = kwargs
    self._done = False
    self._result = None
    self._callback_on_check = callback_on_check or (lambda: None)

  def done(self):
    self._callback_on_check()
    return self._done

  def result(self):
    self._callback_on_check()
    return self._result

  def set_result(self, result):
    self._done = True
    self._result = result


class BatchExecutor(object):
  def __init__(self, batch_functions, num_workers, batch_timeout_sec=10):
    self._num_workers = num_workers
    self._fn_to_batch_fn = batch_functions
    self._fn_futures = dict((fn, []) for fn in self._fn_to_batch_fn)
    self._batch_wait_in_sec = batch_timeout_sec
    self._last_submit = {}

  def _check_results(self, fn):
    if fn in self._last_submit and len(self._fn_futures[fn]):
      if time.time() - self._last_submit[fn] > self._batch_wait_in_sec:
        logger.warning("Flushing incomplete batch of size %d instead of a full batch of size %d due to timeout. "
                       "Consider reducing the batch size." % (len(self._fn_futures[fn]), self._num_workers))
        self._flush(fn)
        self._last_submit[fn] = time.time()

  def _flush(self, fn):
    futures = self._fn_futures[fn][:self._num_workers]
    if len(futures):
      args = list(zip(*[_._args for _ in futures]))
      kwargs = {key: [_._kwargs[key] for _ in futures] for key in futures[0]._kwargs}
      results = self._fn_to_batch_fn[fn](*args, **kwargs)
      if len(results) != len(futures):
        raise ValueError("Wrong number of batch results. Expected %d, got %d" % (len(futures), len(results)))
      for future, result in zip(futures, results):
        future.set_result(result)
      self._fn_futures[fn] = self._fn_futures[fn][self._num_workers:]

  def submit(self, fn, *args, **kwargs):
    if fn not in self._fn_to_batch_fn:
      raise ValueError("There is no known batch version of the function provided")
    batch_future = _BatchFuture(args, kwargs, partial(self._check_results, fn))
    self._fn_futures[fn].append(batch_future)
    if len(self._fn_futures[fn]) >= self._num_workers:
      self._flush(fn)
    self._last_submit[fn] = time.time()
    return batch_future


def _isfinite(value, inf_threshold=GTOPT_POSITIVE_INFINITY):
  values = np.atleast_1d(value).astype(float)
  finite_mask = np.isfinite(values)
  finite_mask[finite_mask] &= np.abs(values[finite_mask]) < inf_threshold
  return finite_mask if np.ndim(value) > 0 else bool(finite_mask[0])


class _Archive(object):
  # CommonConst::NUMERICS_PRECISION from pSeven Core
  PRECISION = np.finfo(np.float64).eps * 1e4

  def __init__(self, input_names, objective_names, constraint_names, payload_objectives, lookup_size=0, cache_size=100):
    self.input_names = input_names
    self.objective_names = objective_names
    self.constraint_names = constraint_names
    self.payload_names = [self.objective_names[i] for i in payload_objectives]
    self.output_names = objective_names + constraint_names
    self.all_names = self.input_names + self.output_names
    self._lookup_size = lookup_size
    self._cache_size = cache_size
    # Internal state of archive
    self._data = dict((_, []) for _ in self.all_names)  # name -> List[value]
    self._n_values = {}  # (name, index) -> int
    self._cache = OrderedDict()  # binary(x) -> idx
    self._size = 0
    self._initial_sample_size = 0
    self.n_history_hits = 0
    self.n_cache_hits = 0

  @property
  def size(self):
    return self._size

  @property
  def init_size(self):
    return self._initial_sample_size

  def register_initial_sample(self, input_sample, output_sample=None):
    if self._size > 0:
      raise ValueError("Can not add initial sample since the evaluation history is not empty. Initial sample should be added first.")
    if input_sample.shape[1] != len(self.input_names):
      raise ValueError("Wrong number of columns in input part of initial sample. Expected %d, got %d." % (len(self.input_names), input_sample.shape[1]))
    if output_sample is not None:
      if output_sample.shape != (input_sample.shape[0], len(self.output_names)):
        raise ValueError("Wrong shape of output part of initial sample. Expected (%d, %d), got %s." % (input_sample.shape[0], len(self.input_names), str(output_sample.shape)))
    for i in np.arange(input_sample.shape[0]):
      if output_sample is None:
        self.store(input_sample[i])
      else:
        self.store(input_sample[i], output_sample[i], np.ones(output_sample.shape[1], dtype=bool))
    self._initial_sample_size = self._size

  def _is_equal(self, index, input):
    # GTOpt treats points x0 and x1 as equal if abs(x0 - x1) <= PRECISION * (1 + min(abs(x0), abs(x1))), so do we
    for i, name in enumerate(self.input_names):
      value1 = input[i]
      value2 = self._data[name][index]
      precision = _Archive.PRECISION * (1 + np.minimum(np.abs(value1), np.abs(value2)))
      if np.abs(value1 - value2) > precision:
        return False
    return True

  def store(self, input, output=None, mask=None):
    index = self.find(input)
    if index is not None:
      # Update existing record with newly calculated values
      self.update(index, output, mask)
      return index

    if len(input) != len(self.input_names):
      raise ValueError("Wrong size of inputs vector. Expected %d, got %d." % (len(self.input_names), len(input)))
    if not np.all(_isfinite(input)):
      raise ValueError("Only finite values are allowed in inputs vector, got %s." % str(input))

    if output is not None:
      if len(output) != len(self.output_names):
        raise ValueError("Wrong size of outputs vector. Expected %d, got %d." % (len(self.output_names), len(output)))
      if mask is None:
        raise ValueError("No outputs mask provided. Expected list of size %d." % len(self.output_names))
      if len(mask) != len(self.output_names):
        raise ValueError("Wrong size of outputs mask. Expected %d, got %d." % (len(self.output_names), len(mask)))

    hash = np.array(input, copy=_SHALLOW).tobytes()
    self._cache[hash] = self._size
    if len(self._cache) > self._cache_size:
      self._cache.popitem(False)
    for i, name in enumerate(self.input_names):
      self._data[name].append(input[i])

    # Payload values are always stored within a list since
    # one point can be associated with multiple payload values,
    if output is None:
      for name in self.output_names:
        self._data[name].append(_NONE)
    else:
      for name, value, calculated in zip(self.output_names, output, mask):
        if name in self.payload_names:
          # Payload is _NONE in case of a missing value, or non-empty tuple otherwise
          self._data[name].append((value,) if calculated and _NONE != value else _NONE)
        else:
          self._data[name].append(value if calculated else _NONE)
    self._size += 1
    return self._size - 1

  def update(self, index, output, mask=None, sparse=False):
    if output is None:
      return
    if mask is None:
      mask = np.ones_like(self.output_names, dtype=bool)

    if index < 0 or index >= self._size:
      raise ValueError("Wrong index of evaluation history item for update. Expected index in range [0, %d), got %d." % (self._size, index))
    if sparse:
      if len(output) != len(mask):
        raise ValueError("Wrong size of sparse outputs mask. Expected %d, got %d." % (len(output), len(mask)))
      if any(output_i < 0 or output_i >= len(self.output_names) for output_i in mask):
        raise ValueError("Wrong index in sparse outputs mask. Expected index in range [0, %d), got %d." % (len(self.output_names), index))
      values = [(self.output_names[m], output[_]) for _, m in enumerate(mask)]
    else:
      if len(output) != len(self.output_names):
        raise ValueError("Wrong size of outputs vector. Expected %d, got %d." % (len(self.output_names), len(output)))
      if len(mask) != len(self.output_names):
        raise ValueError("Wrong size of outputs mask. Expected %d, got %d." % (len(self.output_names), len(mask)))
      values = [(self.output_names[_], output[_]) for _, m in enumerate(mask) if m]

    for name, value in values:
      if name in self.payload_names:
        # Payload is _NONE in case of a missing value, or non-empty tuple otherwise
        if _NONE != value:
          if _NONE != self._data[name][index]:
            value = self._data[name][index] + (value,)
          else:
            value = (value,)
      else:
        if _isfinite(self._data[name][index]) and _isfinite(value):
          # Cumulative average
          n = self._n_values.setdefault((name, index), 1)
          value = float(n * self._data[name][index] + value) / (n + 1)
          self._n_values[(name, index)] += 1
      self._data[name][index] = value

  def get_output(self, index, mask=None):
    if mask is None:
      mask = np.ones_like(self.output_names, dtype=bool)
    elif len(mask) != len(self.output_names):
      raise ValueError("Wrong size of outputs mask. Expected %d, got %d." % (len(self.output_names), len(mask)))

    output = np.empty(sum(mask))
    output.fill(_NONE)
    if index is None:
      return output
    if index < 0 or index >= self._size:
      raise ValueError("Wrong index of evaluation history item for outputs request. Expected index in range [0, %d), got %d." % (self._size, index))

    for i, output_i in enumerate(np.where(mask)[0]):
      name = self.output_names[output_i]
      # We never return a payload value to Nevergrad algorithms
      if name not in self.payload_names:
        output[i] = self._data[name][index]
    return output

  def find(self, input):
    if len(input) != len(self.input_names):
      raise ValueError("Wrong size of inputs vector. Expected %d, got %d." % (len(self.input_names), len(input)))
    if not np.all(_isfinite(input)):
      raise ValueError("Only finite values are allowed in inputs vector, got %s." % str(input))
    index = None
    hash = np.array(input, copy=_SHALLOW).tobytes()
    if hash in self._cache:
      self.n_cache_hits += 1
      index = self._cache[hash]
    elif self._size > 0:
      lookup = self._size if self._lookup_size == 0 else min(self._lookup_size, self._size)
      lookup_mask = np.ones(lookup, dtype=bool)
      # Precision is taken in such way that all points outside are certainly not equal to the given point (w.r.t precision).
      precision = _Archive.PRECISION * (1 + np.amax(np.abs(input)))
      for i, name in enumerate(self.input_names):
        lookup_inputs = np.array(self._data[name][-lookup:])
        submask = np.abs(lookup_inputs[lookup_mask] - input[i]) <= precision
        lookup_mask[lookup_mask] *= submask
        if np.sum(submask) < 2:
          break
      for candidate_index in np.where(lookup_mask)[0]:
        candidate_index = self._size - lookup + candidate_index
        if self._is_equal(candidate_index, input):
          index = candidate_index
          self._cache[hash] = index
          if len(self._cache) > self._cache_size:
            self._cache.popitem(False)
          self.n_history_hits += 1
          break
    return index

  def stack(self, names=None, fill_payloads=True, return_index=False):
    return_1d = False
    if names is None:
      names = np.array(self.all_names)
    else:
      if isinstance(names, str):
        return_1d = True
      names = np.atleast_1d(names).astype(str)
      for name in names:
        if name not in self.all_names:
          raise ValueError("Unknown name %s, expected one of %s." % (name, str(self.all_names)))

    fill_payloads = fill_payloads and any(name in self.payload_names for name in names)
    result = np.empty((self.size, names.size), dtype=object if fill_payloads else float)
    for i, name in enumerate(names):
      # Payload is _NONE in case of a missing value, or non-empty tuple otherwise
      if not fill_payloads and name in self.payload_names:
        result[:, i] = _NONE
      else:
        result[:, i] = self._data[name]

    if return_1d:
      result = result[:, 0]

    if return_index:
      return result, np.arange(self.size)
    else:
      return result


class _Blackbox(object):

  def __init__(self, archive, problem, effective_dim, max_iterations, scalability, batch_size, catvars):
    self.archive = archive
    self.problem = problem
    self.effective_dim = effective_dim
    self.scalability = scalability
    self.batch_size = batch_size
    self.last_error = None
    max_iterations = self.scalability * (max_iterations or np.iinfo(int).max)
    self._evaluation_limits = np.zeros(problem.size_full(), dtype=int)
    for i in range(problem.size_full()):
      limit = problem.elements_hint(problem.size_x() + i, "@GT/EvaluationLimit")
      limit = problem._parse_evaluations_limit(limit)
      if limit == -1:
        self._evaluation_limits[i] = min(max_iterations, np.iinfo(int).max)
      else:
        self._evaluation_limits[i] = min(max_iterations, self.scalability * limit)

    self.catvars = catvars or {}
    self.linear_responses = []
    self.linear_responses_weights = {}  # category -> response index -> weights
    self.n_category_hits = {}

  def set_preprocess_linear_response(self, _preprocess_linear_response, sample_x):
    self._preprocess_linear_response = _preprocess_linear_response
    for i in np.arange(self.problem.size_full()):
      elem_i = self.problem.size_x() + i
      linearity = self.problem.elements_hint(elem_i, "@GTOpt/LinearityType") or "Generic"
      if linearity.lower() == "linear":
        self.linear_responses.append(i)
        self.linear_responses_weights.setdefault(None, {})[i] = []
        weights = self.problem.elements_hint(elem_i, "@GTOpt/LinearParameterVector")
        if weights is not None and len(weights):
          self.linear_responses_weights[None][i] = weights

    if self.linear_responses and sample_x is not None and len(sample_x):
      self._update_categories_hits(sample_x)
      self._restore_linear()

  def _update_categories_hits(self, inputs):
    if not self.catvars:
      categories = [None]
      categories_count = [len(inputs)]
    else:
      cat_idx = sorted(self.catvars)
      cat_inputs, categories_count = np.unique(inputs[:, cat_idx], return_counts=True, axis=0)
      categories = [tuple(_) for _ in cat_inputs]

    for category, count in zip(categories, categories_count):
      self.n_category_hits.setdefault(category, 0)
      self.n_category_hits[category] += count

  def _restore_linear(self):
    if not self.catvars:
      categories = [None]
      # If no categorical variables, request the required points and restore linears on first call
      n_required_points = 1
    else:
      # In case of categorical variables wait for the required sample size
      categories = [category for category in self.n_category_hits]
      n_required_points = self.effective_dim - len(self.catvars) + 2

    categories_to_restore = []
    for category in categories:
      if self.n_category_hits.get(category, 0) >= n_required_points:
        if category not in self.linear_responses_weights:
          categories_to_restore.append(category)
        else:
          responses_weights = self.linear_responses_weights[category]
          if any(not len(_) for _ in responses_weights.values()):
            # Weights of some linear outputs are not known yet in this category
            categories_to_restore.append(category)

    if not categories_to_restore:
      return

    cat_idx = sorted(self.catvars)
    size_x, size_f, size_c = self.problem.size_x(), self.problem.size_f(), self.problem.size_c()
    cat_names = [self.archive.input_names[i] for i in cat_idx]

    for category in categories_to_restore:
      responses_weights = self.linear_responses_weights.setdefault(category, self.linear_responses_weights[None].copy())

      vars_hints = [{} for _ in range(size_x)]  # [{}]*size_x references to the same dict
      objs_hints = [{} for _ in range(size_f)]
      cons_hints = [{} for _ in range(size_c)]

      if category is not None:
        for var_i, var_value in zip(cat_idx, category):
          vars_hints[var_i]["@GT/FixedValue"] = var_value

      for resp_i in self.linear_responses:
        category_hints = objs_hints[resp_i] if resp_i < size_f else cons_hints[resp_i - size_f]
        if resp_i in responses_weights:
          # Never use whole individual budget since if approximation is failed we are out of budget for that response
          category_hints["@GT/EvaluationLimit"] = "Auto"
          category_hints["@GTOpt/LinearParameterVector"] = responses_weights[resp_i]
        else:
          # Disable linear reconstruction of responses that are not requested (or failed before and deleted from the dictionary)
          category_hints["@GTOpt/LinearityType"] = "Generic"

      with self.problem._solve_as_subproblem(vars_hints, objs_hints, cons_hints, doe_mode=False):
        configuration = {
          "batch_size": self.batch_size,
          "evaluations_limit": self._evaluation_limits.tolist(),
          # do not set responses_scalability since it was already used for evaluation limits estimation
        }
        with _limited_evaluations(problem=self.problem, configuration=configuration) as problem:
          sample_x = self.archive.stack(self.problem.variables_names())
          sample_f, sample_c = None, None
          if self.problem.size_f():
            # Ignore payloads for linears reconstruction
            sample_f = self.archive.stack(self.problem.objectives_names(), fill_payloads=False)
          if self.problem.size_c():
            sample_c = self.archive.stack(self.problem.constraints_names())
          if category is not None:
            category_mask = np.all(sample_x[:, cat_idx] == category, axis=1)
            sample_x = sample_x[category_mask]
            if sample_f is not None:
              sample_f = sample_f[category_mask]
            if sample_c is not None:
              sample_c = sample_c[category_mask]
            category_str = ", ".join("%s = %g" % (name, value) for name, value in zip(cat_names, category))
            logger.info(
              "Collected %d points with evaluated linear responses for category %s" % (len(sample_x), category_str)
            )

          hints, evaluations = self._preprocess_linear_response(problem=problem, sample_x=sample_x, sample_f=sample_f, sample_c=sample_c)
          # We can not suggest the new points to the optimizer, since if there are many categorical variables,
          # only those suggested points are going to be calculated (suggested points have higher priority).
          for input, output, mask in zip(*evaluations):
            self.archive.store(input, output, mask)
          # Reduce the limit w.r.t. to scalability, e.g. with scalability N any number K<N of evaluated points counts as N.
          mask_sizes = np.ceil(np.sum(evaluations[-1], axis=0) / self.scalability) * self.scalability
          self._evaluation_limits -= mask_sizes.astype(int)

          for resp_i in list(responses_weights):
            weights = hints[resp_i].get("@GTOpt/LinearParameterVector")
            if weights is not None and len(weights):
              responses_weights[resp_i] = weights
            # Note that weights might be set by user
            if not len(responses_weights[resp_i]):
              # Was not set by user and failed to approximate so dont try again
              del responses_weights[resp_i]

  def _exclude_linear_outputs(self, inputs, mask):
    if not self.catvars:
      categories = [None]
    else:
      cat_idx = sorted(self.catvars)
      cat_inputs = np.unique(inputs[:, cat_idx], axis=0)
      categories = [tuple(_) for _ in cat_inputs]

    calc_mask = np.repeat([mask], len(inputs), axis=0)
    for category in categories:
      if category not in self.linear_responses_weights:
        continue

      if not self.catvars:
        category_mask = np.ones(len(inputs), dtype=bool)
      else:
        category_mask = np.all(inputs[:, cat_idx] == category, axis=1)

      for output_i, weights in self.linear_responses_weights[category].items():
        if len(weights) and mask[output_i]:
          # Disable calculation of linear outputs with known weights
          calc_mask[np.ix_(category_mask, [output_i])] = False

    return calc_mask

  def _fill_linear_outputs(self, inputs, archive_idx, outputs, mask):
    category = None
    category_mask = np.ones(len(inputs), dtype=bool)

    is_calculated = np.zeros(len(inputs), dtype=bool)
    for i, input in enumerate(inputs):
      if np.all(is_calculated[i:]):
        break
      elif is_calculated[i]:
        continue

      if self.catvars:
        cat_idx = sorted(self.catvars)
        category = tuple(input[cat_idx])
        category_mask = np.all(inputs[:, cat_idx] == category, axis=1)

      is_calculated[category_mask] = True

      if category not in self.linear_responses_weights:
        continue

      for i, output_i in enumerate(np.where(mask)[0]):
        weights = self.linear_responses_weights[category].get(output_i, [])
        if len(weights):
          calc_mask = category_mask * (_NONE == outputs[:, i])
          if np.any(calc_mask):
            outputs[calc_mask, i] = np.sum(inputs[calc_mask] * weights[:-1], axis=1) + weights[-1]
            for _ in np.where(calc_mask)[0]:
              sparse_outputs = outputs[_, [i]]
              sparse_mask = [output_i]
              self.archive.update(archive_idx[_], sparse_outputs, sparse_mask, sparse=True)

  def _prepare_mask(self, inputs, mask, restore_linears=True):
    # We can only request all the responses at once (all objectives or all constraints),
    # so estimate the maximum batch size based on the minimum available limit of the masked responses.
    max_batch_size = np.iinfo(int).max
    if np.any(mask):
      max_batch_size = self._evaluation_limits[mask].min() // self.scalability * self.scalability
    if max_batch_size == 0:
      raise errors.NevergradEarlyStopping("Budget limit reached")

    if inputs.ndim != 2 or inputs.shape[1] != self.problem.size_x():
      raise ValueError("Wrong shape of batch inputs. Expected matrix of shape (n x %d), got %s." % (self.problem.size_x(), str(inputs.shape)))

    outputs_mask = np.repeat([mask], inputs.shape[0], axis=0)
    archive_idx = np.empty(inputs.shape[0], dtype=object)
    for i in range(inputs.shape[0]):
      # Add point to archive so that it is available when restoring linear responses
      archive_idx[i] = self.archive.store(inputs[i])
      # Request only unknown values
      output = self.archive.get_output(archive_idx[i])
      outputs_mask[i] *= (_NONE == output)

    if restore_linears and mask[self.linear_responses].any():
      self._update_categories_hits(inputs)
      self._restore_linear()
      # Do not request linear responses that were approximated
      outputs_mask *= self._exclude_linear_outputs(inputs, mask)
      # Check again after linear responses evaluation and reconstruction
      if np.any(mask):
        max_batch_size = self._evaluation_limits[mask].min() // self.scalability * self.scalability
      if max_batch_size == 0:
        raise errors.NevergradEarlyStopping("Budget limit reached")

    # Do not request inputs that have already been calculated
    inputs_mask = np.any(outputs_mask, axis=1)
    # Do not request the same inputs multiple times (remove duplicates from the batch)
    unique_archive_idx = set()
    for i in np.argwhere(inputs_mask).ravel():
      if archive_idx[i] in unique_archive_idx:
        inputs_mask[i] = False
      else:
        unique_archive_idx.add(archive_idx[i])

    # Cut the batch if evaluation limit is reached w.r.t. responses scalability.
    if sum(inputs_mask) > max_batch_size:
      # A point with more requested responses has higher priority. E.g. if we got
      # outputs mask [[True, False], [True, True]] and only 1 point is allowed to request,
      # it has to be the second one.
      points_priority = -np.sum(outputs_mask, axis=1)
      sorted_idx = np.argsort(points_priority)
      inputs_mask[sorted_idx[max_batch_size:]] = False
      if np.any(inputs_mask) and sum(inputs_mask) < self.batch_size:
        logger.warning(
          "Unable to generate a full batch of size %d since evaluation limit has been reached. " % self.batch_size
        )
        logger.debug(
          "The following inputs were excluded from the batch:\n%s" % str(inputs[~inputs_mask].round(3))
        )

    return inputs_mask, outputs_mask, archive_idx

  def evaluate_batch(self, inputs, mask):
    inputs = np.array(inputs)
    inputs_mask, outputs_mask, inputs_archive_idx = self._prepare_mask(inputs, mask)

    if self.last_error is None and np.any(inputs_mask):
      try:
        # Use private `_evaluate` method to track the optimization history for History.csv.
        new_outputs, new_masks = self.problem._evaluate(inputs[inputs_mask], outputs_mask[inputs_mask], timecheck=None)
        new_outputs = np.array(new_outputs, dtype=float)
        new_masks = np.array(new_masks, dtype=bool)
        batch_shape = (sum(inputs_mask), self.problem.size_full())
        if new_outputs.shape != batch_shape:
          raise ValueError("Wrong shape of outputs. Expected %s, got %s." % (str(batch_shape), str(new_outputs.shape)))
        if new_masks.shape != batch_shape:
          raise ValueError("Wrong shape of outputs mask. Expected %s, got %s." % (str(batch_shape), str(new_masks.shape)))
        for i, archive_index in enumerate(inputs_archive_idx[inputs_mask]):
          self.archive.update(archive_index, new_outputs[i], new_masks[i])
        # Reduce the limit w.r.t. to scalability, e.g. with scalability N any number K<N of evaluated points counts as N.
        mask_sizes = np.ceil(np.sum(new_masks, axis=0) / self.scalability) * self.scalability
        self._evaluation_limits -= mask_sizes.astype(int)

        self.last_error = getattr(self.problem, "_last_error", None)
        if self.last_error is not None:
          setattr(self.problem, "_last_error", None)
      except:
        self.last_error = _sys.exc_info()

      if shared._desktop_mode() and self.last_error is not None:
        shared.reraise(*self.last_error) # Useless workaround for the Desktop.

    outputs = np.array([self.archive.get_output(i, mask) for i in inputs_archive_idx])
    if mask[self.linear_responses].any() and self.linear_responses_weights:
      self._fill_linear_outputs(inputs, inputs_archive_idx, outputs, mask)
    return outputs

  def evaluate_from_cache(self, input, mask):
    # Either get the whole output from cache or do nothing
    input = np.array(input)
    if input.ndim != 1 or input.shape[0] != self.problem.size_x():
      raise ValueError("Wrong shape of input vector. Expected vector of size %d, got shape %s." % (self.problem.size_x(), str(input.shape)))
    archive_index = self.archive.find(input)
    if archive_index is None:
      return None
    output = self.archive.get_output(archive_index, mask)
    # Return the value only if all the required values are known
    # hence the blackbox should not be called for that point
    if np.any(_NONE == output):
      return None
    return output


class Objectives(object):

  def __init__(self, blackbox, problem):
    self.blackbox = blackbox
    self.coeffs = []
    self.mask = np.zeros(problem.size_full(), dtype=bool)
    for i in range(problem.size_f()):
      objective_type = problem.elements_hint(problem.size_x() + i, "@GT/ObjectiveType")
      objective_type = 'minimize' if objective_type is None else objective_type.lower()
      if objective_type in ('minimize', 'maximize'):
        self.coeffs.append(1 if objective_type == "minimize" else -1)
        self.mask[i] = True
    # Check that objectives have non-zero evaluation limit if it is not a CSP problem,
    # which is when whether no objectives defined or all of them have zero evaluation limit.
    limits = blackbox._evaluation_limits[self.mask]
    if any(self.mask) and not all(limits == 0):
      if any(limits == 0):
        raise ValueError("One of optimization objectives has zero evaluation limit")
    # Disable mask for no-blackbox objectives
    self.mask *= blackbox._evaluation_limits > 0

  def _safe_rescale(self, values):
    holes_mask = shared._find_holes(values)
    values = np.multiply(values, self.coeffs)
    if holes_mask.any():
      values[holes_mask] = _NONE
    return values

  def calc(self, *args, **kwargs):
    if kwargs.get("cache_only"):
      values = self.blackbox.evaluate_from_cache(input=args, mask=self.mask)
      return None if values is None else np.multiply(values, self.coeffs)

    batch_values = self.blackbox.evaluate_batch(inputs=[args], mask=self.mask)
    return self._safe_rescale(batch_values[0])

  def calc_batch(self, *args):
    batch_values = self.blackbox.evaluate_batch(inputs=np.vstack(args).T, mask=self.mask)
    return self._safe_rescale(batch_values)

  @property
  def n_objectives(self):
    return np.sum(self.mask)


class Constraints(object):

  NG_MAX_VALUE = 4.9e20  # finite value according to NG is < 5e20

  def __init__(self, blackbox, problem, tolerance=1.e-5, cache_size=100):
    self.blackbox = blackbox
    self.problem = problem
    self.bounds = problem.constraints_bounds()
    self.tolerance = tolerance
    self._cache = OrderedDict()  # binary(x) -> violation
    self._cache_size = cache_size
    self.n_cache_hits = 0
    self.mask = np.zeros(problem.size_full(), dtype=bool)
    for i in range(problem.size_c()):
      if not _isfinite(self.bounds[0][i]) and not _isfinite(self.bounds[1][i]):
        raise ValueError("Unbounded constraints are not supported")
      self.mask[problem.size_f() + i] = True
    # Disable mask for no-blackbox constraints
    self.mask *= blackbox._evaluation_limits > 0

  def _calc_batch_violations(self, batch_values):
    unknown_idx = []
    unknown_hashes = []
    batch_violations = np.empty(len(batch_values), dtype=float)
    for i, values in enumerate(batch_values):
      hash = np.array(values, copy=_SHALLOW).tobytes()
      if hash in self._cache:
        self.n_cache_hits += 1
        batch_violations[i] = self._cache[hash]
      else:
        unknown_idx.append(i)
        unknown_hashes.append(hash)
    if unknown_idx:
      mask_c = self.mask[self.problem.size_f():]
      # Fill N/A values if one of constraints has 0 evaluation limit (i.e. is no-blackbox).
      # Note that initial sample points may include values of such constraints.
      if not all(mask_c) and batch_values.shape[1] < self.problem.size_c():
        batch_values_fill_na = np.empty((len(batch_values), self.problem.size_c()), dtype=float)
        batch_values_fill_na[:, mask_c] = batch_values
        batch_values_fill_na[:, ~mask_c] = _NONE
        batch_values = batch_values_fill_na
      violations, _ = self.problem._evaluate_psi(batch_values[unknown_idx], self.tolerance)
      violations[np.isnan(violations)] = Constraints.NG_MAX_VALUE
      violations[violations > Constraints.NG_MAX_VALUE] = Constraints.NG_MAX_VALUE
      violations[violations < -Constraints.NG_MAX_VALUE] = -Constraints.NG_MAX_VALUE
      # Last values is the max violation (might be nan as well)
      violations = violations[:, -1]
      for i, hash, violation in zip(unknown_idx, unknown_hashes, violations):
        self._cache[hash] = batch_violations[i] = violation
        if len(self._cache) > self._cache_size:
          self._cache.popitem(False)
    return batch_violations

  def calc(self, args_kwargs, cache_only=False):
    input = args_kwargs[0]  # we do not use named parameters, just args
    if cache_only:
      values = self.blackbox.evaluate_from_cache(input=input, mask=self.mask)
      batch_values = np.atleast_2d(values)
      return None if values is None else self._calc_batch_violations(batch_values=batch_values)[0]

    batch_values = self.blackbox.evaluate_batch(inputs=[input], mask=self.mask)
    return self._calc_batch_violations(batch_values=batch_values)[0]

  def calc_batch(self, args_kwargs):
    inputs = [_[0] for _ in args_kwargs]  # we do not use named parameters, just args
    batch_values = self.blackbox.evaluate_batch(inputs=inputs, mask=self.mask)
    return self._calc_batch_violations(batch_values=batch_values)


class ObjectivesCSP(Constraints):

  def __init__(self, blackbox, problem, tolerance=1.e-5, cache_size=100, csp_objective_type=None, csp_stop_on_feasible=True):
    super(ObjectivesCSP, self).__init__(blackbox, problem, tolerance, cache_size)
    self.csp_objective_type = csp_objective_type
    self.csp_stop_on_feasible = csp_stop_on_feasible

    lb, ub = np.array(problem.variables_bounds())
    self._init_guess = problem.initial_guess()
    if self._init_guess is None:
      if csp_objective_type is None:
        csp_objective_type = "Psi"
      if csp_objective_type != "Psi":
        raise ValueError("CSP objective type `%s` requires initial guess" % csp_objective_type)
    elif np.isfinite(lb).all() and np.isfinite(ub).all():
      if csp_objective_type is None:
        csp_objective_type = "PsiDistanceNormed"
    else:
      if csp_objective_type is None:
        csp_objective_type = "PsiDistanceInverse"
      if csp_objective_type != "PsiDistanceInverse":
        raise ValueError("CSP objective type `%s` requires bounds of variables" % csp_objective_type)

    if csp_objective_type == "Psi":
      self._calc_objective = lambda batch_values: self._max_psi(batch_values)
      self._n_objectives = 1
    elif csp_objective_type == "PsiDistanceNormed":
      max_vector = np.maximum(self._init_guess - lb, ub - self._init_guess)
      max_dist = max(1, np.hypot.reduce(max_vector))
      self._calc_objective = lambda batch_values: self._max_psi_distance_normed(batch_values, max_dist)
      self._n_objectives = 1
    elif csp_objective_type == "PsiDistanceInverse":
      self._calc_objective = lambda batch_values: self._max_psi_distance_inverse(batch_values)
      self._n_objectives = 1
    else:
      known_types = ", ".join(["Psi", "PsiDistanceNormed", "PsiDistanceInverse"])
      raise ValueError("Unknown CSP objective type `%s`, expencted one of: %s" % (csp_objective_type, known_types))

    self._feasible_point_found = False

  def _max_psi(self, batch_values):
    if self.csp_stop_on_feasible and self._feasible_point_found:
      raise errors.NevergradEarlyStopping("Feasible point found")
    batch_violations = self._calc_batch_violations(batch_values=batch_values)
    if np.any(batch_violations <= 0):
      self._feasible_point_found = True
    return batch_violations

  def _max_psi_distance_normed(self, batch_values, max_dist):
    batch_violations = self._max_psi(batch_values=batch_values)
    feasible_idx = batch_violations <= 0
    if np.any(feasible_idx):
      # Replace 0 values in feasible area with normed to [0, 1] distance to initial guess
      distances = np.hypot.reduce(self._init_guess - batch_values[feasible_idx], axis=1)
      batch_violations[feasible_idx] = -1.0 + distances / max_dist
    return batch_violations

  def _max_psi_distance_inverse(self, batch_values):
    batch_violations = self._max_psi(batch_values=batch_values)
    feasible_idx = batch_violations <= 0
    if np.any(feasible_idx):
      # Replace 0 values in feasible area with inverse distance to initial guess
      distances = np.hypot.reduce(self._init_guess - batch_values[feasible_idx], axis=1)
      batch_violations[feasible_idx] = max(-self.NG_MAX_VALUE, -1.0 / distances)
    return batch_violations

  def calc(self, *args, **kwargs):
    if kwargs.get("cache_only"):
      values = self.blackbox.evaluate_from_cache(input=args, mask=self.mask)
      batch_values = np.atleast_2d(values)
      return None if values is None else self._calc_objective(batch_values=batch_values)[0]

    batch_values = self.blackbox.evaluate_batch(inputs=[args], mask=self.mask)
    return self._calc_objective(batch_values=batch_values)[0]

  def calc_batch(self, *args):
    batch_values = self.blackbox.evaluate_batch(inputs=np.vstack(args).T, mask=self.mask)
    return self._calc_objective(batch_values=batch_values)

  @property
  def n_objectives(self):
    return self._n_objectives


def collect_designs(problem, archive, blackbox):
  size_x = problem.size_x()
  sample, archive_idx = archive.stack(fill_payloads=False, return_index=True)

  if blackbox.linear_responses_weights:
    mask = np.ones(problem.size_full(), dtype=bool)
    inputs = sample[:, :size_x]
    outputs = sample[:, size_x:]

    blackbox._restore_linear()
    blackbox._fill_linear_outputs(inputs, archive_idx, outputs, mask)

  # Remove points that have no evaluated outputs.
  # It can be the case if the final batch was cut
  # due to not enough evaluation limit.
  evaluated_mask = np.any(_NONE != sample[:, size_x:], axis=1)

  for i in problem._payload_objectives:
    col_i = problem.size_x() + i
    name = archive.objective_names[i]
    for row_i, values in enumerate(archive.stack(name)):
      # Payload is _NONE in case of a missing value, or non-empty tuple otherwise
      values = np.atleast_1d(values)
      if values.size == 1:
        if _NONE == values[0]:
          continue
        sample[row_i, col_i] = values[0]
      else:
        value = problem._payload_storage.join_encoded_payloads(values[0], values[1])
        for another_value in values[2:]:
          value = problem._payload_storage.join_encoded_payloads(value, another_value)
        sample[row_i, col_i] = value

  return sample[evaluated_mask]


class _SnapshotFactory(_SolutionSnapshotFactory):

  def __init__(self, archive, blackbox, *args, **kwargs):
    super(_SnapshotFactory, self).__init__(*args, **kwargs)
    self._archive = archive
    self._blackbox = blackbox
    self._last_archive_size = 0

  def snapshot(self, final_result):
    if self._last_snapshot is not None and self._last_archive_size == self._archive.size:
      return self._last_snapshot

    self._last_archive_size = self._archive.size

    try:
      designs_table = collect_designs(problem=self._problem, archive=self._archive, blackbox=self._blackbox)
      status_initial = np.zeros(designs_table.shape[0], dtype=int)
      if not designs_table.size:
        # This must be the first call
        return self._make_snapshot(designs=designs_table,
                                   status_initial=status_initial,
                                   status_feasibility=status_initial,
                                   status_optimality=status_initial)

      status_initial.fill(_SolutionSnapshot._UNDEFINED)
      status_initial[:self._archive.init_size] = _SolutionSnapshot._INITIAL
      status_feasibility = self._status_feasibility(design=designs_table, final_result=final_result)
      status_optimality = self._status_optimality(design=designs_table, status_feasibility=status_feasibility, final_result=final_result)
      return self._make_snapshot(designs=designs_table,
                                 status_initial=status_initial,
                                 status_feasibility=status_feasibility,
                                 status_optimality=status_optimality)
    except:
      pass

    return None


class _ResultFactory(object):
  def __init__(self, solver, problem, archive, blackbox):
    self._solver = solver
    self._problem = problem
    self._archive = archive
    self._blackbox = blackbox
    self._last_result = None
    self._last_state = ()

  def result(self, status, intermediate_result):
    current_state = (self._archive.size, status.id, intermediate_result)
    if self._last_result is not None and current_state == self._last_state:
      return self._last_result
    self._last_state = current_state

    size_x = self._problem.size_x()
    size_f = self._problem.size_f()
    size_c = self._problem.size_c()

    current_options = self._solver.options.values
    constraints_tol = float(self._solver.options.get('GTOpt/ConstraintsTolerance'))
    info = {
      "Solver": {
          "Buildstamp": buildinfo.buildinfo().get("Build", {}).get("Stamp", 'version=' + str(__version__) + ';'),
          "Number of variables": size_x,
          "Number of stochastic variables": 0,
          "Number of objectives": size_f,
          "Number of constraints": size_c,
          "Objectives gradients": False,
          "Constraints gradients": False,
          "Objectives gradients analytical": False,
          "Constraints gradients analytical": False,
          "Options" : dict((k, current_options[k]) for k in current_options if not k.startswith("//")),
      }
    }

    fields, base_offset = [("x", slice(0, size_x))], size_x
    base_offset = _append_field_spec(fields, base_offset, "f", size_f)
    base_offset = _append_field_spec(fields, base_offset, "c", size_c)
    fields = dict(fields)

    n_init = self._archive.init_size
    n_total = self._archive.size
    sample = collect_designs(problem=self._problem, archive=self._archive, blackbox=self._blackbox)

    solutions = sample
    solutions_subsets = {
      "new": slice(n_init, n_total),
      "auto": slice(0, n_total),
      "initial": slice(0, n_init),
    }

    if len(sample):
      sample_x = sample[:, fields["x"]]

      sample_f = []
      if size_f:
        sample_f = sample[:, fields["f"]]
        objectvie_mask = np.zeros(size_f, dtype=bool)
        objectvie_coeff = np.ones(size_f, dtype=int)
        for i in range(size_f):
          objective_type = self._problem.elements_hint(size_x + i, "@GT/ObjectiveType")
          objective_type = 'minimize' if objective_type is None else objective_type.lower()
          if objective_type in ('minimize', 'maximize'):
            objectvie_mask[i] = True
            if objective_type == "maximize":
              objectvie_coeff[i] = -1
        sample_f = sample_f[:, objectvie_mask] * objectvie_coeff[objectvie_mask]

      sample_c, c_bounds = [], []
      if size_c:
        sample_c = sample[:, fields["c"]]
        c_bounds = self._problem.constraints_bounds()

      flag = solution_filter(x=sample_x, f=sample_f, c=sample_c, c_bounds=c_bounds, options=current_options)
      solution_mask = np.zeros(len(sample), dtype=bool)
      solution_mask[flag == GT_SOLUTION_TYPE_CONVERGED] = True
      solution_mask[flag == GT_SOLUTION_TYPE_NOT_DOMINATED] = True
      solutions = sample[solution_mask]
      solutions_n_init = sum(solution_mask[:n_init])
      solutions_n_total = sum(solution_mask)
      solutions_subsets = {
        "new": slice(solutions_n_init, solutions_n_total),
        "auto": slice(0, solutions_n_total),
        "initial": slice(0, solutions_n_init),
      }

    designs = _postprocess_designs(problem=self._problem,
                                   all_designs=sample,
                                   n_initial=n_init,
                                   constraints_tol=constraints_tol)

    result = Result(status=status,
                    info=info,
                    solutions=solutions,
                    solutions_subsets=solutions_subsets,
                    fields=fields,
                    problem=_weakref.ref(self._problem),
                    designs=designs,
                    finalize=False)

    result._finalize(problem=self._problem,
                     auto_objective_type="Minimize",
                     options=current_options,
                     logger=self._solver._get_logger(),
                     intermediate_result=intermediate_result)

    self._last_result = result
    self._last_archive_size = self._archive.size
    return result


class Watcher(object):
  def __init__(self, solver, problem, archive, blackbox, call_interval=3):
    self._archive = archive
    self._previous_best = None
    self._call_interval = call_interval
    self._next_call_time = time.time() + self._call_interval
    self._user_watcher = solver._get_watcher()
    self._log = solver._log
    self._blackbox_ref = _weakref.ref(blackbox)
    self._result_factory = _ResultFactory(
      solver=solver,
      problem=problem,
      archive=archive,
      blackbox=blackbox,
    )
    self._snapshot_factory = _SnapshotFactory(
      archive=archive,
      generator=solver,
      problem=problem,
      blackbox=blackbox,
      watcher=lambda msg=None: True,
      auto_objective_type="minimize",
    )
    if len(self._archive.all_names) != self._snapshot_factory._designs_width - 1:
      self._log(
        LogLevel.DEBUG,
        "WARN: Wrong shape of history matrix for intermediate result %d!=%d"
        % (len(self._archive.all_names), self._snapshot_factory._designs_width - 1)
      )

    self.keep_going = True
    self.last_error = None

  def __call__(self, ng_optimizer, *args, **kwargs):
    if self.last_error is None:
      self.last_error = getattr(self._blackbox_ref(), "last_error", None)
      if self.last_error is not None:
        self.keep_going = False

    if time.time() > self._next_call_time and self.keep_going:

      best_value = None
      if ng_optimizer.num_objectives == 1:
        loss = ng_optimizer.provide_recommendation().loss
        best_value = np.array([loss]) if loss is not None else None
      elif ng_optimizer.num_objectives > 1:
        best_value = np.array([_.loss for _ in ng_optimizer.pareto_front()])

      self.keep_going = self._call_user_watcher(best_value)
      self._next_call_time = time.time() + self._call_interval

    if not self.keep_going:
      # We can only stop normally on `ask` callback when no args set.
      # Values of parameters and loss are only set on `tell` callback.
      if not args and not kwargs:
        error_message = "Optimization process stopped by user"
        try:
          if self.last_error is not None:
            error_message = ''.join(shared._format_user_only_exception(*self.last_error))
        except:
          pass
        self._log(LogLevel.DEBUG, error_message)
        raise errors.NevergradEarlyStopping(error_message)

  def _call_user_watcher(self, best_value, status=IN_PROGRESS, final_result=False):
    if self._user_watcher is None:
      return True

    result_updated = False
    if best_value is not None:
      if self._previous_best is None or len(self._previous_best) != len(best_value):
        self._previous_best = best_value
        result_updated = True
      else:
        diff = np.abs(np.subtract(self._previous_best, best_value))
        if np.any(diff > 1e-10):
          self._previous_best = best_value
          result_updated = True

    lazy_result = _DetachableSingleCallableRef(
      callable=self._result_factory.result,
      status=status,
      intermediate_result=True,  # Never evaluate responses from watcher call
    )
    lazy_snapshot = _DetachableSingleCallableRef(
      callable=self._snapshot_factory.snapshot,
      final_result=final_result
    )
    return self._user_watcher({
      "ResultUpdated": result_updated if not final_result else True,
      "RequestIntermediateResult": lazy_result,
      "RequestIntermediateSnapshot": lazy_snapshot,
    })


class LogHandler(logging.Handler):
  def __init__(self, solver):
    super(LogHandler, self).__init__()
    self.solver = solver

  def emit(self, record):
    msg = self.format(record)
    if record.levelno <= logging.DEBUG:
      self.solver._log(LogLevel.DEBUG, msg)
    elif record.levelno == logging.INFO:
      self.solver._log(LogLevel.INFO, msg)
    elif record.levelno == logging.WARN:
      self.solver._log(LogLevel.WARN, msg)
    elif record.levelno >= logging.ERROR:
      self.solver._log(LogLevel.ERROR, msg)


def collect_parameters(problem):
  catvars = {}
  parameters = []
  effective_dim = 0
  initial_guess = problem.initial_guess()
  for i in range(problem.size_x()):
    bound = problem.variables_bounds(i)
    variable_type = problem.elements_hint(i, "@GT/VariableType")
    fixed_value = problem.elements_hint(i, "@GT/FixedValue")
    variable_type = "continuous" if variable_type is None else variable_type.lower()
    if fixed_value is not None:
      parameter = float(fixed_value)
    elif len(bound) == 1 or np.all(bound[0] == bound[1:]):
      parameter = float(bound[0])
    elif variable_type == "continuous" or variable_type == "integer":
      effective_dim += 1
      bound = bound.astype(object)
      bound[~_isfinite(bound)] = None
      # Initial guess is already in bounds and rounded for integer variables
      init = None if initial_guess is None else initial_guess[i]
      parameter = nevergrad.p.Scalar(init=init, lower=bound[0], upper=bound[1])
      if variable_type == "integer":
        parameter = parameter.set_integer_casting()
    elif variable_type == "stepped" or variable_type == "discrete":
      effective_dim += 1
      parameter = nevergrad.p.TransitionChoice(choices=bound)
    elif variable_type == "categorical":
      catvars[i] = bound
      effective_dim += 1
      parameter = nevergrad.p.Choice(choices=bound)
    parameters.append(parameter)
  return parameters, catvars, effective_dim


def estimate_budget(max_iterations, effective_dim, responses_scalability, batch_size):
  if max_iterations == 0:
    budget = np.clip(10 * effective_dim ** 2, 100, 10000)
    budget = int(np.ceil(budget / 100) * 100)
  else:
    budget = max_iterations

  scaled_budget = budget
  if responses_scalability > 1:
    scaled_budget *= responses_scalability

  if batch_size > 0:
    # Round up to batch size, it will be cut at runtime by evaluation limits
    scaled_budget = (scaled_budget + batch_size - 1) // batch_size * batch_size

  return int(scaled_budget)


def _test_categorical_only_problem(problem, scaled_budget, factor_types):
  """
  Since we are not forcing Nevergad to check the whole categorical subspace, all non-continous variables
  ([Transition]Choice variables in terms of Nevergrad) are considered here: categorical, discrete, stepped.
  In contrast, since GTOpt runs an independent study for each combination of categorical values,
  the method `solver._test_categorical_only_problem` checks cardinality of the categorical subspace only.
  """
  n_combinations, size_x = 1, problem.size_x()
  n_infinite = 1024 * 1024 * 128 // size_x  # No more than 1G in memory

  variables_type = problem.elements_hint(slice(0, size_x), "@GT/VariableType")
  for i, variable_type in enumerate(variables_type):
    variable_type = str(variable_type or "continuous").lower()
    variable_bounds = problem.variables_bounds(i)
    if variable_type in factor_types:
      n_levels = len(variable_bounds)
      if n_levels > 1:
        n_combinations = (n_levels * n_combinations) if (n_infinite // n_combinations) >= n_levels else n_infinite
    elif variable_type in ("discrete", "stepped"):
      if len(variable_bounds) > 1:
        return False  # the problem can be solved, somehow...
    else:
      # Check that bounds are not equal for continuous variable.
      # Note that @GT/FixedValue hint is converted to equal bounds as well.
      if np.isnan(variable_bounds).any() or variable_bounds[0] < variable_bounds[1]:
        return False # the problem can be solved, somehow...

  return n_combinations < n_infinite and n_combinations <= scaled_budget


def validate(solver, problem, sample_x=None, sample_f=None, sample_c=None):
  diagnostics = []

  max_iterations = int(solver.options.get("GTOpt/MaximumIterations"))
  batch_size = int(solver.options.get("GTOpt/BatchSize"))
  responses_scalability = int(solver.options.get("GTOpt/ResponsesScalability"))

  def error(msg):
    diagnostics.append(diagnostic.DiagnosticRecord(diagnostic.DIAGNOSTIC_ERROR, msg))

  def warn(msg):
    diagnostics.append(diagnostic.DiagnosticRecord(diagnostic.DIAGNOSTIC_WARNING, msg))

  def hint(msg):
    diagnostics.append(diagnostic.DiagnosticRecord(diagnostic.DIAGNOSTIC_HINT, msg))

  def misc(msg):
    diagnostics.append(diagnostic.DiagnosticRecord(diagnostic.DIAGNOSTIC_MISC, msg))

  def _loose_version_string(code):
    return ".".join(str(_) for _ in code) if code else "<no version>"

  current_version = _distutils_loose_version(nevergrad.__version__)
  supported_versions = sorted([_distutils_loose_version("0.13.0"), _distutils_loose_version("1.0.8")])
  if current_version < supported_versions[0]:
    error('Nevergrad version %s is not supported! Required version >= %s' % (_loose_version_string(current_version), _loose_version_string(supported_versions[0])))
  elif current_version > supported_versions[-1]:
    hint('Detected newer version of Nevergrad %s (tested with %s) - consider checking the release notes.' % (_loose_version_string(current_version), _loose_version_string(supported_versions[-1])))

  if problem.objectives_gradient()[0] or problem.constraints_gradient()[0]:
    error("Nevergrad does not support gradients of objectives and constraints in problem definition")
  if problem.size_nf() or problem.size_nc() or problem.size_s():
    error("Nevergrad does not support stochastic variables in problem definition")

  parameters, catvars, effective_dim = collect_parameters(problem)
  if effective_dim == 0:
    error("At least one (free) design variable should be specified.")

  if batch_size == 0:
    batch_size = responses_scalability if responses_scalability > 1 else np.clip(effective_dim, 2, 10)

  if responses_scalability > batch_size:
    error("Target scalability %d can not be reached with batch size %d." % (responses_scalability, batch_size))

  if responses_scalability > 1:
    batch_size = batch_size // responses_scalability * responses_scalability

  scaled_budget = estimate_budget(max_iterations=max_iterations,
                                  effective_dim=effective_dim,
                                  responses_scalability=responses_scalability,
                                  batch_size=batch_size)

  factor_types = ("categorical", "discrete", "stepped")
  if _test_categorical_only_problem(problem, scaled_budget=scaled_budget, factor_types=factor_types):
    with shared._suppress_history(problem):
      status, diagnostics = solver._build_full_factorial(problem=problem,
                                                         mode=api.GTOPT_VALIDATE,
                                                         sample_x=sample_x,
                                                         sample_f=sample_f,
                                                         sample_c=sample_c,
                                                         compatibility=False,
                                                         factor_types=factor_types)
      return ValidationResult(status, diagnostics)

  budget_msg = "%d blackbox calls" % (scaled_budget // responses_scalability)
  if responses_scalability > 1:
    budget_msg += " with %d parallel executors or %d evaluations in total" % (responses_scalability, scaled_budget)
  if batch_size > 1:
    budget_msg += " (%d batches of size %d)" % (scaled_budget // batch_size, batch_size)
  budget_msg = "Final exploration budget: %s\n" % budget_msg
  hint(budget_msg)

  try:
    blackbox = _Blackbox(archive=None,
                         problem=problem,
                         effective_dim=effective_dim,
                         max_iterations=max_iterations,
                         scalability=responses_scalability,
                         batch_size=batch_size,
                         catvars=catvars)
    objectives = Objectives(blackbox=blackbox, problem=problem)
    constraints = Constraints(blackbox=blackbox, problem=problem)

    has_bb_objectives = np.any(objectives.mask)
    has_bb_constraints = np.any(constraints.mask)
    if not has_bb_objectives and not has_bb_constraints:
      error("At least one optimization objective or constraint must be defined with non-zero evaluation limit")

    if objectives.n_objectives > 5:
      # Nevergrad minimizes hypervolume, which is recalculated with the complexity of O(n^(d-2)*log(n)) each time the Pareto-front is changed.
      # An Improved Dimension-Sweep Algorithm for the Hypervolume Indicator
      # https://ieeexplore.ieee.org/document/1688440
      warn("Too many objectives, low performance expected. The current technique is known to show weak performance in multi-objective problems")

  except Exception as ex:
    error(str(ex))

  try:
    sample_x, sample_f, sample_c, output_sample = prepare_samples(problem, sample_x, sample_f, sample_c)
    if sample_x is None:
      if sample_f is not None or sample_c is not None:
        warn("Initial sample is ignored since the input part of the sample is missing")
    problem._validate_linear_responses(sample_x, sample_f, sample_c)
  except Exception as ex:
    error(str(ex))

  misc(json.dumps({
    "_details": {
      "Optimization": {
        "N_eval": int(scaled_budget),
        "batch_size": int(batch_size),
      },
    }
  }))

  if any(_.severity == diagnostic.DIAGNOSTIC_ERROR for _ in diagnostics):
    status = UNSUPPORTED_PROBLEM
  else:
    status = SUCCESS

  return ValidationResult(status, diagnostics)


def prepare_samples(problem, sample_x, sample_f, sample_c):
  output_sample = None
  if sample_x is not None:
    sample_x = np.atleast_2d(sample_x).astype(float) if np.ndim(sample_x) > 1 else np.array(sample_x, dtype=float).reshape(-1, 1)
    if sample_x.shape[1] != problem.size_x():
      raise ValueError("Wrong number of columns in input part of initial sample. Expected %d, got %d." % (problem.size_x(), sample_x.shape[1]))

    if sample_f is not None or sample_c is not None:
      dtype = object if problem._payload_objectives and sample_f is not None else float
      output_sample = np.empty((sample_x.shape[0], problem.size_full()), dtype=dtype)

      if sample_f is None:
        output_sample[:, :problem.size_f()] = _NONE
      else:
        sample_f = np.atleast_2d(sample_f) if np.ndim(sample_x) > 1 else np.array(sample_x, dtype=object).reshape(-1, 1)
        # It can be a None value, which should be properly interpreted as a Hole, otherwise it is converted to NaN.
        sample_f[_NONE == sample_f] = _NONE
        sample_f = sample_f.astype(dtype)
        if sample_f.shape != (sample_x.shape[0], problem.size_f()):
          raise ValueError("Wrong shape of objectives part of initial sample. Expected (%d, %d), got %s." % (sample_x.shape[0], problem.size_f(), str(sample_f.shape)))
        output_sample[:, :problem.size_f()] = sample_f

      if sample_c is None:
        output_sample[:, problem.size_f():] = _NONE
      else:
        sample_c = np.atleast_2d(sample_c) if np.ndim(sample_x) > 1 else np.array(sample_x, dtype=object).reshape(-1, 1)
        # It can be a None value, which should be properly interpreted as a Hole, otherwise it is converted to NaN.
        sample_c[_NONE == sample_c] = _NONE
        sample_c = sample_c.astype(float)
        if sample_c.shape != (sample_x.shape[0], problem.size_c()):
          raise ValueError("Wrong shape of constraints part of initial sample. Expected (%d, %d), got %s." % (sample_x.shape[0], problem.size_c(), str(sample_c.shape)))
        output_sample[:, problem.size_f():] = sample_c

  return sample_x, sample_f, sample_c, output_sample


@_contextlib.contextmanager
def _wrap_with_archive(problem, blackbox, batch_size):
  configuration = {
    "batch_size": batch_size,
    "evaluations_limit": blackbox._evaluation_limits.tolist(),
    # do not set responses_scalability since it was already used for evaluation limits estimation
  }
  with _limited_evaluations(problem=problem, configuration=configuration) as problem:
    original_evaluate = problem._evaluate

    def _evaluate_with_archive(inputs, full_mask, *args, **kwargs):
      # TODO : check blackbox.last_error
      inputs = np.array(inputs)

      # For now let us ignore rare cases of partial requests,
      # when a column in the mask might contain True not for all inputs.
      mask = np.any(full_mask, axis=0)
      if getattr(blackbox, "last_error", None) is not None:
        # Disable requests after exception
        eval_mask = np.zeros_like(mask)
      else:
        # Disable request for outputs with not enough budget
        eval_mask = mask * blackbox._evaluation_limits >= blackbox.scalability
      # Do not allow restoring linears to avoid recursion when requesting new points:
      #  _prepare_mask -> _preprocess_linear_response -> _evaluate_with_archive -> _prepare_mask
      inputs_mask, outputs_mask, inputs_archive_idx = blackbox._prepare_mask(inputs, eval_mask, restore_linears=False)

      if np.any(inputs_mask):
        # Use private `_evaluate` method to track the optimization history for History.csv.
        new_outputs, new_masks = original_evaluate(inputs[inputs_mask], outputs_mask[inputs_mask], timecheck=None)
        new_outputs = np.array(new_outputs, dtype=float)
        new_masks = np.array(new_masks, dtype=bool)
        batch_shape = (sum(inputs_mask), blackbox.problem.size_full())
        if new_outputs.shape != batch_shape:
          raise ValueError("Wrong shape of outputs. Expected %s, got %s." % (str(batch_shape), str(new_outputs.shape)))
        if new_masks.shape != batch_shape:
          raise ValueError("Wrong shape of outputs mask. Expected %s, got %s." % (str(batch_shape), str(new_masks.shape)))
        for i, archive_index in enumerate(inputs_archive_idx[inputs_mask]):
          blackbox.archive.update(archive_index, new_outputs[i], new_masks[i])
        # Reduce the limit w.r.t. to scalability, e.g. with scalability N any number K<N of evaluated points counts as N.
        mask_sizes = np.ceil(np.sum(new_masks, axis=0) / blackbox.scalability) * blackbox.scalability
        blackbox._evaluation_limits -= mask_sizes.astype(int)

      outputs = np.array([blackbox.archive.get_output(i, mask) for i in inputs_archive_idx])
      if mask[blackbox.linear_responses].any() and blackbox.linear_responses_weights:
        blackbox._fill_linear_outputs(inputs, inputs_archive_idx, outputs, mask)

      full_outputs = np.empty_like(full_mask, dtype=float)
      full_outputs.fill(_NONE)
      full_outputs[:, mask] = outputs
      return full_outputs, _NONE != full_outputs

    problem._evaluate = _evaluate_with_archive

    try:
      yield problem
    finally:
      if original_evaluate is not None and problem._evaluate is not original_evaluate:
        problem._evaluate = original_evaluate


def solve(solver, problem, sample_x=None, sample_f=None, sample_c=None):
  # Redirect Nevergrad loggers
  redirected_logger = LogHandler(solver)
  logger.addHandler(redirected_logger)
  nevergrad.optimizers.logger.addHandler(redirected_logger)
  try:
    return _solve(solver, problem, sample_x, sample_f, sample_c)
  finally:
    # Restore Nevergrad loggers
    logger.removeHandler(redirected_logger)
    nevergrad.optimizers.logger.removeHandler(redirected_logger)


def _solve(solver, problem, sample_x, sample_f, sample_c):
  solver._log(LogLevel.INFO, "Solving by Nevergrad %s the following %s" % (nevergrad.__version__, str(problem)))

  max_iterations = int(solver.options.get("GTOpt/MaximumIterations"))
  seed = int(solver.options.get("GTOpt/Seed")) if shared.parse_auto_bool(solver.options.get("GTOpt/Deterministic"), True) else np.random.randint(1, 65535)
  verbosity = int(shared.parse_auto_bool(solver.options.get("GTOpt/VerboseOutput"), False))
  time_limit = int(solver.options.get("GTOpt/TimeLimit"))
  batch_size = int(solver.options.get("GTOpt/BatchSize"))
  responses_scalability = int(solver.options.get("GTOpt/ResponsesScalability"))
  constraints_tolerance = float(solver.options.get('GTOpt/ConstraintsTolerance'))
  restore_linear = shared.parse_auto_bool(solver.options.get("GTOpt/RestoreAnalyticResponses"), "auto")

  lookup_size = int(solver.options.values.get("/GTOpt/Nevergrad/HistoryLookupSize", 0))
  cache_size = int(solver.options.values.get("/GTOpt/Nevergrad/HistoryCacheSize", 100))
  verbosity = int(solver.options.values.get("/GTOpt/Nevergrad/Verbosity", verbosity))
  watcher_call_interval = float(solver.options.values.get("/GTOpt/Nevergrad/WatcherCallInterval", 3))
  enable_hypervolume = shared.parse_bool(solver.options.values.get("/GTOpt/Nevergrad/EnableHyperVolume", True))
  set_objectives_number = shared.parse_bool(solver.options.values.get("/GTOpt/Nevergrad/SetNumberOfObjectives", False))  # Changes algorithm selection path, usually selects DE when set
  multiobjective_reference = shared.parse_json(solver.options.values.get("/GTOpt/Nevergrad/MultiobjectiveReference"))
  csp_objective_type = solver.options.values.get("/GTOpt/Nevergrad/CSPObjectiveType")
  csp_stop_on_feasible = shared.parse_bool(solver.options.values.get("/GTOpt/Nevergrad/CSPStopOnFeasible", True))
  n_unique_sampling_attempts = int(solver.options.values.get("/GTOpt/Nevergrad/UniqueSamplingAttempts", 10))

  for msg in validate(solver, problem, sample_x, sample_f, sample_c).details:
    if msg.severity == diagnostic.DIAGNOSTIC_ERROR:
      raise exceptions.InvalidProblemError(msg.message)
    elif msg.severity == diagnostic.DIAGNOSTIC_WARNING:
      solver._log(LogLevel.WARN, msg.message)
    elif msg.severity == diagnostic.DIAGNOSTIC_HINT:
      solver._log(LogLevel.INFO, msg.message)

  parameters, catvars, effective_dim = collect_parameters(problem)

  if batch_size == 0:
    batch_size = responses_scalability if responses_scalability > 1 else np.clip(effective_dim, 2, 10)

  # Validation assures that batch_size >= responses_scalability
  if responses_scalability > 1:
    batch_size = batch_size // responses_scalability * responses_scalability

  scaled_budget = estimate_budget(max_iterations=max_iterations,
                                  effective_dim=effective_dim,
                                  responses_scalability=responses_scalability,
                                  batch_size=batch_size)

  archive = _Archive(input_names=problem.variables_names(),
                     objective_names=problem.objectives_names(),
                     constraint_names=problem.constraints_names(),
                     payload_objectives=problem._payload_objectives,
                     lookup_size=lookup_size,
                     cache_size=cache_size)

  blackbox = _Blackbox(archive=archive,
                       problem=problem,
                       effective_dim=effective_dim,
                       max_iterations=max_iterations,
                       scalability=responses_scalability,
                       batch_size=batch_size,
                       catvars=catvars)
  objectives = Objectives(blackbox=blackbox, problem=problem)
  constraints = Constraints(blackbox=blackbox, problem=problem, tolerance=constraints_tolerance)

  has_bb_objectives = np.any(objectives.mask)
  has_bb_constraints = np.any(constraints.mask)
  if not has_bb_objectives:
    if has_bb_constraints:
      objectives = ObjectivesCSP(blackbox=blackbox, problem=problem, tolerance=constraints_tolerance,
                                 csp_objective_type=csp_objective_type, csp_stop_on_feasible=csp_stop_on_feasible)
      solver._log(LogLevel.DEBUG, "No objectives set, switching to CSP problem with %s objectives" % objectives.csp_objective_type)

  factor_types = ("categorical", "discrete", "stepped")
  if _test_categorical_only_problem(problem, scaled_budget=scaled_budget, factor_types=factor_types):
    with _limited_evaluations(problem=problem, configuration={"batch_size": batch_size}) as problem:
      solution_snapshot_watcher = solver._create_snapshot_watcher(problem=problem, mode=api.GTOPT_SOLVE)
      solution_snapshot_watcher.initial_sample(sample_x=sample_x,
                                               sample_f=sample_f,
                                               sample_c=sample_c,
                                               sample_nf=None,
                                               sample_nc=None)
      with shared._suppress_history(problem):
        result = solver._build_full_factorial(problem=problem,
                                              mode=api.GTOPT_SOLVE,
                                              sample_x=sample_x,
                                              sample_f=sample_f,
                                              sample_c=sample_c,
                                              compatibility=False,
                                              factor_types=factor_types)

      solution_snapshot_watcher.report_final_result(result=result,
                                                    sample_x=sample_x,
                                                    sample_f=sample_f,
                                                    sample_c=sample_c,
                                                    sample_nf=None,
                                                    sample_nc=None)
    return result

  parametrization = nevergrad.p.Instrumentation(*parameters)
  parametrization.random_state.seed(seed)
  optimizer = BatchOptimizer(parametrization=parametrization,
                             budget=scaled_budget,
                             num_workers=batch_size)

  if set_objectives_number:
    optimizer.num_objectives = objectives.n_objectives
  if not enable_hypervolume:
    optimizer._no_hypervolume = True
  if multiobjective_reference:
    optimizer.tell(nevergrad.p.MultiobjectiveReference(), multiobjective_reference)

  sample_x, sample_f, sample_c, output_sample = prepare_samples(problem, sample_x, sample_f, sample_c)
  if sample_x is not None:
    # Round values and mark those that are out of bounds/levels
    sample_x, is_valid = problem._valid_input_points(sample_x, precision=8)
    # Encode payload values
    if output_sample is not None:
      for i in problem._payload_objectives:
        output_sample[:, i] = problem._payload_storage.encode_payload(output_sample[:, i], None)
    # Save raw unrounded values to history, otherwise we would need to fix archive lookup
    archive.register_initial_sample(input_sample=sample_x, output_sample=output_sample)
    for x_vector in sample_x[is_valid]:
      optimizer.suggest(*x_vector)
      optimizer.budget += 1
  if problem.initial_guess() is not None:
    # In some cases initial guess set by Nevergrad parameters may be ignored
    # (i.g. continuous variable with no bounds) so we explicitly pass it to optimizer
    optimizer.suggest(*problem.initial_guess())
    optimizer.budget += 1

  if restore_linear:
    blackbox.set_preprocess_linear_response(
      partial(solver._preprocess_linear_response,
              mode=api.GTOPT_SOLVE,
              return_evaluations=True),
      sample_x=sample_x,
    )

  progress_callback = None
  try:
    from tqdm import tqdm

    class Log(object):
      def write(self, msg):
        solver._log(LogLevel.INFO, msg)
      def flush(self):
        pass

    progress_callback = nevergrad.callbacks.ProgressBar()
    progress_callback._progress_bar = tqdm(file=Log(), ascii=True)
    progress_callback._progress_bar.total = optimizer.budget
    optimizer.register_callback("tell", progress_callback)
  except Exception as ex:
    solver._log(LogLevel.INFO, "Can not set progress bar, consider installing tqdm: %s" % str(ex))

  executor = BatchExecutor(batch_functions={objectives.calc: objectives.calc_batch,
                                            constraints.calc: constraints.calc_batch},
                           num_workers=optimizer.num_workers,
                           batch_timeout_sec=10)

  result_status = SUCCESS
  with shared.sigint_watcher(solver):
    watcher = Watcher(solver=solver, archive=archive, problem=problem, blackbox=blackbox, call_interval=watcher_call_interval)
    optimizer.register_callback("ask", watcher)
    optimizer.register_callback("tell", watcher)
    if time_limit:
      optimizer.register_callback("ask", nevergrad.callbacks.EarlyStopping.timer(time_limit))

    try:
      # Batch mode is always enabled since in terms of Nevergrad it means
      # to wait for the whole batch to be calculated before generating new points
      optimizer.minimize(objective_function=objectives.calc,
                         executor=executor,
                         batch_mode=True,
                         verbosity=verbosity,
                         constraint_violation=[constraints.calc] if has_bb_objectives and has_bb_constraints else None,
                         n_unique_sampling_attempts=n_unique_sampling_attempts)
    except errors.NevergradEarlyStopping as ex:
      # Catch early stopping exceptions threw at "tell" stage from response calculation functions,
      # since Nevergrad handles such exceptions only from watcher, i.e. threw at "ask" stage
      solver._log(LogLevel.INFO, "Optimization was stopped: %s" % str(ex))

    if progress_callback is not None:
      progress_callback._progress_bar.close()
    if not watcher.keep_going:
      result_status = INVALID_PROBLEM if watcher.last_error else USER_TERMINATED

    # Since the blackbox is called directly, the values of evaluated responses need
    # to be saved to the archive so that the final result contains the whole sample.
    solver._log(LogLevel.INFO, "Finalizing the result data...")
    with _wrap_with_archive(
      problem=problem,
      blackbox=blackbox,
      # Use the option value directly - if it is 0 then all the points are requested at once
      batch_size=int(solver.options.get("GTOpt/BatchSize")),
    ) as archived_problem:
      result_factory = _ResultFactory(solver=solver, problem=archived_problem, archive=archive, blackbox=blackbox)
      result = result_factory.result(status=result_status, intermediate_result=False)

    # In the case of 'user terminated' status it is not allowed to call watcher anymore,
    # so the sigint wrapper will suppress this call and the last snapshot will be
    # inconsistent with the result, which is OK (same as for other p7core techniques).
    watcher._call_user_watcher(best_value=None, status=result_status, final_result=True)

  if blackbox.last_error is not None and not len(result.designs()):
    shared.reraise(*blackbox.last_error)

  return result
