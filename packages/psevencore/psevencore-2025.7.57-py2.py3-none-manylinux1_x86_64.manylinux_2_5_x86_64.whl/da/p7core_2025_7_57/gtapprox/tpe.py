#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import numpy as np

from ..six.moves import range

def sampling_space(approx_options, technique, random_state):
  space = {}
  if technique.lower() != 'gbrt':
    for option in approx_options:
      bounds = approx_options.get_bounds(option)
      if option['type'] == 'Continuous':
        space[option] = lambda x: random_state.uniform(bounds[0], bounds[1], size=x)
      elif option['type'] == 'Integer':
        space[option] = lambda x: random_state.randint(bounds[0], bounds[1], size=x)
      elif option['type'] == 'Enum':
        space[option] = lambda x: random_state.choice(bounds, size=x)

  else:
    max_depth = approx_options.get_bounds('GTApprox/GBRTMaxDepth')
    if max_depth:
      space['GTApprox/GBRTMaxDepth'] = lambda x: qloguniform(max_depth[0], max_depth[1], x, 1, random_state)

    min_child_weight = approx_options.get_bounds('GTApprox/GBRTMinChildWeight')
    if max_depth:
      space['GTApprox/GBRTMinChildWeight'] = lambda x: sum(min_child_weight) - qloguniform(min_child_weight[0], min_child_weight[1],
                                                                                           x, 1, random_state)

    min_loss_reduction = approx_options.get_bounds('GTApprox/GBRTMinLossReduction')
    if min_loss_reduction:
      space['GTApprox/GBRTMinLossReduction'] = lambda x: random_state.uniform(min_loss_reduction[0], min_loss_reduction[1], x)

    n_trees = approx_options.get_bounds('GTApprox/GBRTNumberOfTrees')
    if n_trees:
      space['GTApprox/GBRTNumberOfTrees'] = lambda x: sum(n_trees) - qloguniform(n_trees[0], n_trees[1], x, 5, random_state)
      # space['GTApprox/GBRTNumberOfTrees'] = lambda x: quniform(n_trees[0], n_trees[1], x, 1, random_state)

    shrinkage = approx_options.get_bounds('GTApprox/GBRTShrinkage')
    if shrinkage:
      # space['GTApprox/GBRTShrinkage'] = lambda x: loguniform(shrinkage[0], shrinkage[1], x, random_state)
      space['GTApprox/GBRTShrinkage'] = lambda x: random_state.uniform(shrinkage[0], shrinkage[1], x)

    subsample_ratio = approx_options.get_bounds('GTApprox/GBRTSubsampleRatio')
    if subsample_ratio:
      space['GTApprox/GBRTSubsampleRatio'] = lambda x: sum(subsample_ratio) - loguniform(subsample_ratio[0], subsample_ratio[1],
                                                                                         x, random_state)
    col_sample_ratio = approx_options.get_bounds('GTApprox/GBRTColsampleRatio')
    if col_sample_ratio:
      space['GTApprox/GBRTColsampleRatio'] = lambda x: random_state.uniform(col_sample_ratio[0], col_sample_ratio[1], x)

  return space


def get_optimizer(problem, time_limit, seed=None, estimate_objective_time=True):
  random_state = np.random.RandomState(seed)

  if estimate_objective_time:
    _ = problem.define_objectives(problem.init_x)

  technique = problem.fixed_options['GTApprox/Technique'].lower()
  training_time = problem.objective_time_estimate

  n_evaluations = np.inf
  average_training_time_ratio = 1
  if 'gbrt' == technique:
    if 'GTApprox/GBRTNumberOfTrees' in problem.opt_options:
      average_n_trees = np.mean(problem.opt_options.get_bounds('GTApprox/GBRTNumberOfTrees', [1]))
      init_n_trees = problem.opt_options.get_init_value('GTApprox/GBRTNumberOfTrees',
                                                        int(problem.approx_builder.options.get('GTApprox/GBRTNumberOfTrees')))
      average_training_time_ratio = average_n_trees / float(init_n_trees)

    if np.isfinite(time_limit):
      n_evaluations = 10  # minimal number of iterations in case of strict time limits
    else:
      n_evaluations = 60  # with probability 95% we will hit into region of top 5% of optimum

  if 'moa' == technique:
    n_evaluations = len(problem.opt_options.get_bounds('GTApprox/MoANumberOfClusters')) - 1

  if np.isfinite(time_limit):
    max_number_of_evaluations = max(int(time_limit / float(training_time)), n_evaluations)
  else:
    max_number_of_evaluations = n_evaluations

  if training_time * n_evaluations * average_training_time_ratio > time_limit:
    optimizer = lambda x: random_optimizer(x, budget=max_number_of_evaluations, random_state=random_state)
  else:
    optimizer = None

  return optimizer, max_number_of_evaluations


def random_optimizer(problem, budget=60, random_state=None):
  """
  Optimize using TPE algorithm
  """
  if not random_state:
    random_state = np.random.RandomState()

  x_dim = len(problem.variables_names())
  space = sampling_space(problem.opt_options, problem.fixed_options['GTApprox/Technique'], random_state)

  sample = np.empty((budget, x_dim), dtype=float)

  for i in range(x_dim):
    generate = space[problem.variables_names()[i]]
    sample[:, i] = generate(budget)

  for x in sample:
    problem.define_objectives(x)


def tpe_optimizer(problem, budget=60, random_state=None):
  """
  Optimize by random sampling
  """
  if not random_state:
    random_state = np.random.RandomState()

  x_dim = len(problem.variables_names())
  space = sampling_space(problem.opt_options, problem.fixed_options['GTApprox/Technique'], random_state)

  sample = np.empty((budget, x_dim), dtype=float)

  initial_size = 20
  for i in range(x_dim):
    generate = space[problem.variables_names()[i]]
    sample[:initial_size, i] = generate(initial_size)

  rrms = []
  for x in sample[:initial_size]:
    rrms.append(problem.define_objectives(x))

  # TPE-like optimization
  n_candidates = 1000
  n_points = initial_size
  while n_points < budget:
    candidates_sample = np.empty((n_candidates, x_dim), dtype=float)
    for i, variable in enumerate(problem.variables_names()):
      bounds = problem.opt_options.get_bounds(variable)
      if problem.opt_options[variable]['type'] == 'Continuous':
        candidates_sample[:, i] = random_state.uniform(bounds[0], bounds[1], size=n_candidates)
      else:
        candidates_sample[:, i] = random_state.randint(bounds[0], bounds[1], size=n_candidates)

    EI = expected_improvement(sample[:n_points], rrms[:n_points], 0.15, candidates_sample)

    sample[n_points] = candidates_sample[np.argmax(EI)]
    rrms.append(problem.define_objectives(sample[n_points]))
    n_points += 1


def loguniform(lower, upper, size, random_state):
  sample = random_state.uniform(np.log(lower), np.log(upper), size=size)
  return np.exp(sample)


def qloguniform(lower, upper, size, quantization, random_state):
  sample = np.round(loguniform(lower, upper, size, random_state) / quantization) * quantization
  return sample


def quniform(lower, upper, size, quantization, random_state):
  sample = random_state.uniform(lower, upper, size)
  return np.round(sample / quantization) * quantization


def expected_improvement(x, y, gamma, t):
  indices = y < np.percentile(y, gamma * 100)

  def parzen_estimator(sorted_sample, x):
    right_neighbors = np.minimum(np.searchsorted(sorted_sample, x, side='right'), len(sorted_sample) - 1)
    left_neighbors = np.maximum(np.searchsorted(sorted_sample, x, side='left') - 1, 0)
    distance_to_farthest_neighbor = np.maximum(sorted_sample[right_neighbors] - x, x - sorted_sample[left_neighbors])
    mean_distance = (sorted_sample[-1] - sorted_sample[0]) / float(len(sorted_sample))
    sigmas = np.minimum(2 * mean_distance, distance_to_farthest_neighbor)

    pdf = np.zeros((len(x),))
    for i, x_center in enumerate(sorted_sample):
      pdf += _normpdf(x, x_center, sigmas[i])

    return pdf

  EI = 1

  for column in range(x.shape[1]):
    x_more_optimal = np.sort(x[indices, column], axis=0)
    x_less_optimal = np.sort(x[~indices, column], axis=0)
    EI *= parzen_estimator(x_more_optimal, t[:, column]) / parzen_estimator(x_less_optimal, t[:, column])

  return EI


def _normpdf(x, mu, sigma):
  u = (x - mu) / float(sigma)
  return np.exp(-u * u / 2.0) / (np.sqrt(2 * np.pi) * sigma)
