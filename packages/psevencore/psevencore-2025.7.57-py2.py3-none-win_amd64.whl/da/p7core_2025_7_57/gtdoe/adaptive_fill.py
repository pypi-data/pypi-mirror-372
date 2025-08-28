#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#


"""Auxiliary functions for adaptive fill. """

from numpy import isfinite as _isfinite

from ..six import iteritems
from ..gtopt.solver import Solver as _Optimizer
from ..gtopt.solver import ValidationResult
from ..gtopt import diagnostic as _diagnostic
from .. import exceptions as _ex
from .. import shared as _shared
from .. import loggers as _loggers
from .. import status as _status
from ..gtopt import api as _api
from ..gtopt.problem import _limited_evaluations

def _fill(generator, blackbox, count, search_intensity=None, level=None,
          init_x=None, init_y=None, sample_x=None, sample_f=None, sample_c=None, time_limit=0,
          options=None, validation_mode=False):

  optimizer = _Optimizer()
  if options:
    generator.options.set(options)

  count = int(count)
  if count < 0:
    raise ValueError("The number of points to generate must be greater than or equal to zero: count=%s" % count)

  optimizer.options.set(_translate_general_options(generator, optimizer))

  #explicitly set parameters overwrite options
  if search_intensity is None or not _isfinite(search_intensity):
    search_intensity = generator.options.get("GTDoE/AdaptiveDesign/SearchIntensity")
  optimizer.options.set("GTOpt/GlobalPhaseIntensity", search_intensity)

  #optimizer.options.set("GTOpt/BatchSize", generator.options.get("/GTDoE/BatchSize")) # all private options are translated
  optimizer.options.set('GTOpt/ResponsesScalability', generator.options.get('GTDoE/ResponsesScalability'))
  optimizer.options.set('GTOpt/DetectNaNClusters', generator.options.get('GTDoE/AdaptiveDesign/DetectNaNClusters'))
  optimizer.options.set('GTOpt/MaximumIterations', generator.options.get('GTDoE/AdaptiveDesign/MaximumIterations'))
  optimizer.options.set('GTOpt/MaximumExpensiveIterations', generator.options.get('GTDoE/AdaptiveDesign/MaximumExpensiveIterations'))
  optimizer.options.set('GTOpt/RestoreAnalyticResponses', generator.options.get('GTDoE/AdaptiveDesign/RestoreAnalyticResponses'))

  if level is None or not _isfinite(level):
    level = _shared.parse_float(generator.options.get("GTDoE/AdaptiveDesign/ContourLevel")) #get returns str!

  if level is not None and _isfinite(level):
    optimizer.options.set("/GTOpt/ContourLevel", level)
  optimizer.options.set("/GTOpt/DesignPointsCount", count)
  if time_limit:
    optimizer.options.set("GTOpt/TimeLimit", time_limit)
  optimizer.set_logger(generator._logger)
  optimizer.set_watcher(generator._watcher)
  if (init_x is not None or init_y is not None) and (sample_x is not None or sample_f is not None or sample_c is not None):
    raise _ex.WrongUsageError("'init_*' and 'sample_*' can not be used together.")
  if init_x is not None:
    sample_x = init_x
    if init_y is not None:
      guessesResponses = _shared.as_matrix(init_y, shape=(None, (blackbox.size_f() + blackbox.size_c())), dtype=None, order='A', name="Initial sample of objective and/or constraint function(s) values ('init_y' argument)")
      sample_f = guessesResponses[:, :blackbox.size_f()] if blackbox.size_f() else None
      sample_c = guessesResponses[:, blackbox.size_f():] if blackbox.size_c() else None

  kwargs = {"sample_x": sample_x, "sample_f": sample_f, "sample_c": sample_c, "compatibility": False}

  try:
    if sample_f is not None and blackbox._payload_storage and blackbox._payload_objectives:
      decoded_sample_f = sample_f.astype(object)
      for i in blackbox._payload_objectives:
        decoded_sample_f[:, i] = blackbox._payload_storage.decode_payload(sample_f[:, i])
      kwargs["sample_f"] = decoded_sample_f
  except:
    pass

  if validation_mode:
    status, diagnostics = optimizer._run_solver(blackbox, _api.GTOPT_VALIDATE_DOE, **kwargs)
    return ValidationResult(status, diagnostics)

  maximum_expensive_iterations = int(optimizer.options.get('GTOpt/MaximumExpensiveIterations'))
  maximum_iterations = int(optimizer.options.get('GTOpt/MaximumIterations'))
  responses_scalability = int(optimizer.options.get('GTOpt/ResponsesScalability'))
  configuration = optimizer._read_limited_evaluations_configuration(options={})

  with _limited_evaluations(problem=blackbox, maximum_iterations=maximum_iterations, maximum_expensive_iterations=maximum_expensive_iterations,
                            sample_x=sample_x, sample_f=sample_f, sample_c=sample_c, watcher_ref=optimizer._get_watcher, configuration=configuration) as problem:
    result = optimizer._run_solver(problem, _api.GTOPT_DOE, **kwargs)

  try:
    if generator._logger:
      n_generated = result._solutions_size("feasible") if count else 0
      if count != n_generated:
        generator._logger(_loggers.LogLevel.WARN, "`AdaptiveDesign` technique generated %d feasible points, %d points were requested." % (n_generated, count))
  except:
    pass # just ignore
  return result

def _translate_general_options(generator, optimizer=None):
  if optimizer is None:
    optimizer = _Optimizer()

  translation_prefixes = ('/gtdoe/optimizer/', '/gtdoe/')

  generator_options = generator.options.values
  for k in generator_options:
    k_lower = k.lower()
    for prefix in translation_prefixes:
      if k_lower.startswith(prefix):
        try:
          # try to map option from gtdoe to gtopt
          optimizer.options.set("GTOpt/" + k[len(prefix):], generator_options[k])
          break
        except:
          pass # intentionally do nothing
    else:
      if k.startswith("/"):
        optimizer.options.set(k, generator_options[k])    #does not need any order, hidden options will get priority inside c++ code anyway

  # explicitly set this option due to different defaults for DoE and optimization mode
  optimizer.options.set("/GTOpt/EvaluateResultSubset", generator.options.get("/GTDoE/EvaluateResultSubset"))

  return optimizer.options.values

def _test_categorical_only_problem(problem):
  return _Optimizer._test_categorical_only_problem(problem, True)

def _read_constraints_tolerance(generator):
  optimizer = _Optimizer()
  _translate_general_options(generator, optimizer)
  return float(optimizer.options.get("GTOpt/ConstraintsTolerance"))

def _report_validation_failure(exc_type, exc_info, exc_tb):
  return ValidationResult(exc_info, [_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_ERROR, str(exc_info))])

def _report_validation_succeeded(n_doe, n_init, report, status):
  if n_doe is not None:
    report.setdefault("_details", {}).setdefault("DoE", {})["N_doe"] = n_doe
  if n_init is not None:
    report.setdefault("_details", {}).setdefault("Adaptive", {})["N_train"] = n_init
  subproblems = dict(report.get("_details", {})) # make shallow copy
  subproblems["CategoricalSignature"] = {}
  subproblems["CategoricalName"] = ""
  report["_subproblems"] = [subproblems]
  return ValidationResult(_status.SUCCESS, [_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_MISC, str(_shared.write_json(report)))])

class _IssuesCollectionLogger(object):
  def __init__(self):
    self._issues = []

  def __call__(self, level, message):
    if level == _loggers.LogLevel.WARN:
      self._issues.append(_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_WARNING, message))
    elif level > _loggers.LogLevel.WARN:
      self._issues.append(_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_ERROR, message))

  @property
  def issues(self):
    return self._issues
