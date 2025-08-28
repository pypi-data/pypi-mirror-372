#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import ctypes as _ctypes

import numpy as np

from .. import exceptions as _ex
from .. import shared as _shared
from .. import options as _options
from ..six import b as _bytes
from ..six import string_types, iteritems
from ..six.moves import xrange
from ..utils import _fdist
from .core_ic import _generate_fronts, _MultiRoute
from .technique_selection import TechniqueSelector, _get_unique_elements, _build_inputs_encoding_model
from .utilities import Utilities
from .cluster import _init_clusters_center


class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.c_size_ptr = _ctypes.POINTER(_ctypes.c_size_t)
    self.c_double_ptr = _ctypes.POINTER(_ctypes.c_double)
    self.c_byte_ptr = _ctypes.POINTER(_ctypes.c_byte)

    self.select_subsample = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_size_t, _ctypes.c_size_t,
                                              _ctypes.c_size_t, self.c_double_ptr, self.c_size_ptr,
                                              _ctypes.c_size_t, self.c_double_ptr, self.c_size_ptr,
                                              self.c_byte_ptr, _ctypes.c_size_t, _ctypes.c_char_p,
                                              _ctypes.POINTER(_ctypes.c_void_p))(('GTApproxUtilitiesSelectSubsampleCART', self.__library))

_api = _API()

def _setup_random_state(split_method, seed):
  method = str(split_method).lower()
  if method == "random":
    return np.random.RandomState(seed)
  elif method == "auto":
    return "cart" if seed is None else np.random.RandomState(seed)
  elif method in ("cart", "duplex", "ks"):
    return method
  else:
    raise ValueError("Invalid or unsupported dataset split method is given: %s" % split_method)

def _check_random_state(random_state):
  if random_state is None:
    return True
  elif isinstance(random_state, string_types):
    return str(random_state).lower() in ("auto", "random", "cart", "duplex", "ks")
  return hasattr(random_state, 'permutation')

def _read_sample_size(sample_size):
  try:
    # Ugly, but avoids the false positive identification of 1.0 as an integer
    if np.issubdtype(type(sample_size), np.floating):
      return float(sample_size), "f"
  except:
    pass

  try:
    if int(sample_size) == float(sample_size):
      return int(sample_size), "i"
  except:
    pass

  try:
    return float(sample_size), "f"
  except:
    pass

  return sample_size, None

def train_test_split(x, y, train_size=None, test_size=None, options=None):
  """
  Split a data sample into train and test subsets optimized for model training.

  :param x: sample inputs (values of variables)
  :param y: sample responses (function values)
  :param train_size: optional number of training points (``int``) or portion of the sample to include in the train subset (``float``)
  :param test_size: optional number of test points (``int``) or portion of the sample to include in the test subset (``float``)
  :param options: option settings
  :type x: :term:`array-like`, 1D or 2D
  :type y: :term:`array-like`, 1D or 2D
  :type options: ``dict``
  :type train_size: ``int`` or ``float``
  :type test_size: ``int`` or ``float``
  :return: tuple of train inputs, test inputs, train outputs and test outputs
  :rtype: ``tuple``

  Performs an optimized split of the given data sample into two subsets to be used
  as model training and validation (test) data.
  The distribution of points between train and test is optimized to create subsets
  that both provide good representation of input and response variance,
  aiming to avoid skew, which may be introduced by random split.
  """

  options_manager = _options._OptionManager('GTApprox/')
  options_impl = _options.Options(options_manager.pointer, None)
  if options is not None:
    _shared.check_concept_dict(options, 'options')
    options_impl.set(options)
  explicit_options = set(_.lower() for _ in options_impl.values)

  def _get_option(name, alt_default, postprocess=None):
    value = options_impl.get(name) # validate option name and value if any
    if str(name).lower() in explicit_options:
      return postprocess(value) if postprocess is not None else value
    return alt_default

  metainfo_template = _shared.create_metainfo_template(x, y, options=options_impl.values)
  categorical_inputs_map, categorical_outputs_map = _shared.read_categorical_maps(metainfo_template)

  sample_size = np.shape(x)[0]
  train_ratio, test_ratio = None, None

  if train_size is not None:
    train_size, value_type = _read_sample_size(train_size)
    if (value_type not in ("i", "f")
        or value_type == "i" and (train_size >= sample_size or train_size <= 0)
        or value_type == "f" and (train_size <= 0 or train_size >= 1)):
      raise ValueError("Invalid train_size argument. Expected an integer in (0, %d) or a float in (0.0, 1.0)" % sample_size)
    elif value_type == "i":
      train_ratio = float(train_size) / sample_size
    elif value_type == "f":
      train_ratio = train_size

  if test_size is not None:
    test_size, value_type = _read_sample_size(test_size)
    if (value_type not in ("i", "f")
        or value_type == "i" and (test_size >= sample_size or test_size <= 0)
        or value_type == "f" and (test_size <= 0 or test_size >= 1)):
      raise ValueError("Invalid test_size argument. Expected an integer in (0, %d) or a float in (0.0, 1.0)" % sample_size)
    elif value_type == "i":
      test_ratio = float(test_size) / sample_size
    elif value_type == "f":
      test_ratio = test_size

  x_data = _shared.encode_categorical_values(x, categorical_inputs_map, 'input') if categorical_inputs_map else x
  y_data = _shared.encode_categorical_values(y, categorical_outputs_map, 'output') if categorical_outputs_map else y

  fixed_structure, tensor_structure = False, _get_option("GTApprox/TensorFactors", None, _shared.parse_json)
  if _get_option("GTApprox/EnableTensorFeature", False, _shared.parse_bool):
    if tensor_structure is not None:
      if not Utilities.checkTensorStructure(x, tensor_structure)[0]:
        raise ValueError("The data sample does not match specified tensor factors %s" % str(tensor_structure))
      fixed_structure = True
    else:
      tensor_structure = Utilities.checkTensorStructure(x)[1]
      if not tensor_structure:
        tensor_structure = None
  else:
    tensor_structure = None

  base_subsample = None

  random_state = np.random.RandomState(_get_option("GTApprox/Seed", None, int))
  split_method = str(options_impl.get('//TrainTestSplit/Method')).lower()

  if train_ratio is None and test_ratio is None:
    ratio = 0
  elif test_ratio is None:
    ratio = train_ratio
  elif train_ratio is None:
    ratio = 1.0 - test_ratio
  elif abs(train_ratio + test_ratio - 1) < 1e-6:
    ratio = train_ratio
  elif (train_ratio + test_ratio) < 1. and not tensor_structure:
    # select subsample using cart method in deterministic mode
    base_subsample, _, _ = _train_test_split(x_data, y_data, (train_ratio + test_ratio),
                                            tensor_structure=tensor_structure, fixed_structure=fixed_structure,
                                            random_state=("cart" if _get_option("GTApprox/Deterministic", False, _shared.parse_bool) else random_state),
                                            categorical_inputs_map=categorical_inputs_map, categorical_outputs_map=categorical_outputs_map, user_options=options)
    ratio = train_ratio / (train_ratio + test_ratio)
  else:
    raise ValueError("The sum of train_size and test_size arguments must be either 1.0 or the sample size %d" % sample_size)

  # update random state
  if split_method == "auto":
    if ratio and _shared.parse_bool(options_impl.get("GTApprox/Deterministic")):
      random_state = "cart" # use cart in non-adaptive, deterministic mode
  elif split_method in ("cart", "duplex", "ks"):
    random_state = split_method
  elif split_method != "random":
    raise ValueError("Invalid or unsupported dataset split method is given: %s" % split_method)

  train_indices, test_indices, tensor_structure = _train_test_split(x_data if base_subsample is None else x_data[base_subsample],
                                                                    y_data if base_subsample is None else y_data[base_subsample],
                                                                    ratio, tensor_structure=tensor_structure,
                                                                    fixed_structure=fixed_structure,
                                                                    random_state=random_state,
                                                                    categorical_inputs_map=categorical_inputs_map,
                                                                    categorical_outputs_map=categorical_outputs_map,
                                                                    user_options=options,
                                                                    min_factor_size=int(options_impl.get('//TrainTestSplit/MinFactorSize')),
                                                                    # These options are used in Adaptive split method only
                                                                    train_neighbors_ratio=_shared.parse_float(options_impl.get('//TrainTestSplit/Adaptive/TrainNeighborsRatio')),
                                                                    max_curvature=_shared.parse_float(options_impl.get('//TrainTestSplit/Adaptive/MaxFrontCurvature')),
                                                                    max_n_points=int(options_impl.get('//TrainTestSplit/Adaptive/MaxSampleSize')),
                                                                    min_test_size=1)

  if base_subsample is not None:
    subsample_train_indices, subsample_test_indices = train_indices, test_indices
    train_indices, test_indices = base_subsample.copy(), base_subsample.copy()
    train_indices[base_subsample] = subsample_train_indices
    test_indices[base_subsample] = subsample_test_indices

  def subsample(sample, idx):
    try:
      return sample.iloc[idx] if hasattr(sample, 'iloc') else sample[idx]
    except:
      pass

    try:
      return [sample[_] for _ in np.where(idx)[0]]
    except:
      pass

    return _shared.as_matrix(sample)[idx]

  return subsample(x, train_indices), subsample(x, test_indices), subsample(y, train_indices), subsample(y, test_indices)

def select_subsample(x, y, ratio, detect_tensor_structure=False, seed=None, method="auto", return_tensor_structure=False,
                     tensor_structure=None, categorical_inputs_map=None, categorical_outputs_map=None,
                     min_factor_size=5, train_neighbors_ratio=0.3, max_curvature=0.3, max_n_points=10000):
  """
  This method splits given training sample into train/test subsets and returns train and test indices of the subsets.

  :param x: training sample, input part (values of variables)
  :param y: training sample, response part (function values)
  :param ratio: training subsample size to full sample size ratio (default value 0 enables the adaptive ratio control).
  :param detect_tensor_structure: should we detect tensor structure (maybe long) or not.
  :param seed: optional seed for random generator.
  :param method: method of dataset splitting. One of the "auto", "random", "cart", "duplex" or "ks" strings. If method is "auto" then splitting method is RANDOM if seed is given otherwise the CART method is used.
  :param return_tensor_structure: indicates whether to return tensor structure found as the last element of tuple. Tensor structure is a list (may be empty) of lists containing axes of the cartesian factors.
  :type x: :term:`array-like`, 1D or 2D
  :type y: :term:`array-like`, 1D or 2D
  :type ratio: ``float`` in range [0, 1)
  :type detect_tensor_structure: ``bool``
  :type seed: ``int``
  :type return_tensor_structure: ``bool``
  :return: tuple of train and test indices and optionally the tensor structure found
  :rtype: ``tuple(1D numpy array, 1D numpy array)`` or ``tuple(1D numpy array, 1D numpy array, list of lists)``
  """
  # Note that the method although not public but is used in platform
  if categorical_inputs_map:
    x = _shared.encode_categorical_values(x, categorical_inputs_map, 'input')
  if categorical_outputs_map:
    y = _shared.encode_categorical_values(y, categorical_outputs_map, 'output')

  fixed_structure = False
  if detect_tensor_structure:
    if tensor_structure is not None:
      if not Utilities.checkTensorStructure(x, tensor_structure)[0]:
        raise ValueError("The dataset given doesn't have the proposed tensor structure %s" % str(tensor_structure))
      fixed_structure = True
    else:
      tensor_structure = Utilities.checkTensorStructure(x)[1]
      if not tensor_structure:
        tensor_structure = None
  else:
    tensor_structure = None

  random_state = _setup_random_state(split_method=method, seed=seed)
  train_indices, test_indices, tensor_structure = _train_test_split(x, y, ratio,
                                                                    tensor_structure=tensor_structure,
                                                                    fixed_structure=fixed_structure,
                                                                    random_state=random_state,
                                                                    categorical_inputs_map=categorical_inputs_map,
                                                                    categorical_outputs_map=categorical_outputs_map,
                                                                    min_factor_size=min_factor_size,
                                                                    train_neighbors_ratio=train_neighbors_ratio,
                                                                    max_curvature=max_curvature,
                                                                    max_n_points=max_n_points)

  if return_tensor_structure:
    return np.where(train_indices)[0], np.where(test_indices)[0], (tensor_structure if tensor_structure else [])
  else:
    return np.where(train_indices)[0], np.where(test_indices)[0]

def _train_test_split(x, y, train_test_ratio, tensor_structure=None, fixed_structure=False, min_factor_size=5, random_state=None,
                      categorical_inputs_map=None, categorical_outputs_map=None, max_curvature=0.3, train_neighbors_ratio=0.3,
                      max_n_points=10000, min_test_size=None, user_options=None, dry_run=False):
  train_test_ratio = _shared.parse_float(train_test_ratio)
  if not (train_test_ratio >= 0. and train_test_ratio < 1.):
    raise ValueError('The train/test subsample ratio %g is out of valid [0, 1) range' % train_test_ratio)

  if not _check_random_state(random_state):
    raise ValueError('The random generator given is not None nor one of the ["auto", "random", "cart", "duplex", "ks"] strings and has no \'permutation\' method')

  # standard sample conformance checks
  x = _shared.as_matrix(x, name="Input part of the dataset ('x' argument)")
  y = _shared.as_matrix(y, name="Output part of the dataset ('y' argument)")

  if x.shape[0] != y.shape[0]:
    raise ValueError('The number of x vectors does not match the number of y vectors: %s != %s' % (x.shape[0], y.shape[0]))

  if 1 == x.shape[0]:
    raise ValueError('The dataset given cannot be split because it contains single vector only.')
  elif 2 == x.shape[0]:
    # degenerated case
    return np.array([True, False], dtype=bool), np.array([False, True], dtype=bool), tensor_structure

  y = _encode_sample_dummy(categorical_outputs_map, y)

  if not train_test_ratio and dry_run == 'quick':
    train_test_ratio = 0.8

  if tensor_structure is not None:
    # get factor sizes
    factor_train_sizes, tensor_structure, unique_x = _get_new_factors(x, train_test_ratio, x.shape[0], min_factor_size,
                                                                      tensor_structure, fixed_structure)
    if 0.0 == train_test_ratio:
      train_indices = _get_adaptive_tensor_subsample(x, y, unique_x, tensor_structure, max_curvature=max_curvature)
    else:
      # get subsample of each factor
      train_indices = _get_tensor_sample_subsample(x, unique_x, tensor_structure, factor_train_sizes, random_state)

  if tensor_structure is None or (not fixed_structure and np.all(train_indices)):
    x = _encode_input_sample(categorical_inputs_map, x, y, user_options)
    if 0.0 == train_test_ratio:
      train_indices = _adaptive_split(x, y, random_state=random_state, max_curvature=max_curvature,
                                      train_neighbors_ratio=train_neighbors_ratio, max_n_points=max_n_points,
                                      min_test_size=min_test_size, dry_run=dry_run)
      # adaptive split produced test sample with biased variance - try to use alternatives
      if not train_indices.all() and not _test_split_variance(train=y[train_indices], test=y[~train_indices]):
        subsample_size, adjustment_range = np.count_nonzero(train_indices), int(np.ceil(x.shape[0] * 0.1))
        min_subsample_size, max_subsample_size = max(3, subsample_size - adjustment_range), min(x.shape[0] - 3, subsample_size + adjustment_range)
        candidates = np.unique([subsample_size] + np.round(np.linspace(min_subsample_size, max_subsample_size, max(0, min(10, max_subsample_size - min_subsample_size)))).astype(int).tolist())
        candidates = sorted(candidates, key=lambda x: 2*abs(subsample_size - x)+(x > subsample_size))
        # now try to lil modify ratio
        for alt_subsample_size in candidates:
          alt_train_indices = _select_subsample(alt_subsample_size, x, y, random_state)
          if _test_split_variance(train=y[alt_train_indices], test=y[~alt_train_indices]):
            train_indices = alt_train_indices
            break
    else:
      train_indices = _select_subsample(max(0, int(x.shape[0] * train_test_ratio)), x, y, random_state)

  test_indices = np.invert(train_indices)

  return train_indices, test_indices, tensor_structure

def _encode_sample_dummy(categorical_variables_map, sample):
  if not categorical_variables_map:
    return sample

  original_variables = []
  categorical_variables = []
  encoded_variable_dim = 0
  for i in np.arange(sample.shape[1]):
    if i in categorical_variables_map:
      categorical_variables.append(i)
      encoded_variable_dim += len(categorical_variables_map[i][2]) - 1
    else:
      original_variables.append(i)
      encoded_variable_dim += 1

  encoded_sample = np.zeros((sample.shape[0], encoded_variable_dim))

  shift = 0
  for i in categorical_variables:
    dtype, labels, enumerators = categorical_variables_map[i]
    forbidden_values = np.ones(sample.shape[0], dtype=bool)
    for j, enumerator in enumerate(enumerators[:-1]):
      mask = sample[:, i] == enumerator
      encoded_sample[mask, shift] = 1
      forbidden_values[mask] = False
      shift += 1
    forbidden_values[sample[:, i] == enumerators[-1]] = False

    if np.any(forbidden_values):
      encoded_sample[forbidden_values, shift - len(enumerators) + 1: shift] = sample[forbidden_values, i]

  encoded_sample[:, shift:] = sample[:, original_variables]

  return encoded_sample

def _encode_input_sample(categorical_inputs_map, x, y, options=None):
  if not categorical_inputs_map:
    return x

  options_manager = _options._OptionManager('GTApprox/')
  options_impl = _options.Options(options_manager.pointer, None)
  options_impl.set('GTApprox/CategoricalVariables', [_ for _ in categorical_inputs_map])

  if options is not None:
    _shared.check_concept_dict(options, 'options')
    options_impl.set(options)

  if '//Encoding/InputsEncoding' not in options_impl.values:
    technique_selector = TechniqueSelector(options_impl, None)
    encoding = technique_selector.select_encoding(x, y, technique='auto', allowed_techniques=None, initial_model=None)
    options_impl.set('//Encoding/InputsEncoding', encoding)

  encoding_model = _build_inputs_encoding_model(x, y, options_impl, weights=None, tol=None, initial_model=None)
  return encoding_model.calc(x) if encoding_model else _encode_sample_dummy(categorical_inputs_map, x)

def _select_subsample(subsample_size, x, y, random_state):
  # additional paranoid assertion
  if 0 > subsample_size:
    raise ValueError('Invalid subsample size is given: %d' % subsample_size)

  sel = np.zeros((x.shape[0],), dtype=bool)

  if not random_state:
    method = _ctypes.c_char_p(_bytes("cart"))
  elif not isinstance(random_state, string_types):
    sel[random_state.permutation(len(x))[:subsample_size]] = True
    return sel
  elif random_state.lower() == "random":
    sel[np.random.permutation(len(x))[:subsample_size]] = True
    return sel
  elif random_state.lower() in ("cart", "auto"):
    method = _ctypes.c_char_p(_bytes("cart"))
  elif random_state.lower() == "duplex":
    method = _ctypes.c_char_p(_bytes("duplex"))
  elif random_state.lower() == "ks":
    method = _ctypes.c_char_p(_bytes("ks"))
  else:
    raise ValueError('Invalid or unsupported subsample selection method is given: %s' % random_state)

  x = _shared.as_matrix(x, name="Input part of the dataset ('x' argument)")

  if y is not None:
    y = _shared.as_matrix(y, name="Output part of the dataset ('y' argument)")
    if x.shape[0] != y.shape[0]:
      raise ValueError('The number of x vectors does not match the number of y vectors: %s != %s' % (x.shape[0], y.shape[0]))
  else:
    y = np.empty((0, 0), dtype=float)

  err_desc = _ctypes.c_void_p()

  if not _api.select_subsample(x.shape[0], subsample_size,
                               x.shape[1], x.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(x.ctypes.strides, _api.c_size_ptr),
                               y.shape[1], y.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(y.ctypes.strides, _api.c_size_ptr),
                               sel.ctypes.data_as(_api.c_byte_ptr), sel.strides[0] // sel.itemsize,
                               method, _ctypes.byref(err_desc)):
    _shared.ModelStatus.checkErrorCode(0, 'Failed to select subsample', err_desc)

  return sel

def _test_split_variance(train, test, alpha=0.1):
  eps = np.finfo(float).eps**0.5

  for train_i, test_i in zip(train.T, test.T):
    train_i, test_i = train_i[np.isfinite(train_i)], test_i[np.isfinite(test_i)]
    if len(train_i) < 3 or len(test_i) < 3:
      return False

    var_train = np.var(train_i, ddof=1)
    var_test = np.var(test_i, ddof=1)

    F_stat = (var_train + eps) / (var_test + eps)
    F_distr = _fdist(len(train_i) - 1, len(test_i) - 1)

    F_min = F_distr.quantile(0.5*alpha, complement=False)
    F_max = F_distr.quantile(0.5*alpha, complement=True)

    if F_stat < F_min or F_stat > F_max:
      return False

  return True


def _map_duplicates(x):
  finite_x = np.isfinite(x).all(axis=1)
  all_finite = finite_x.all()

  order = np.lexsort(x.T if all_finite else x[finite_x].T)
  unique_marks = np.hstack(([True], (x[order[1:]] != x[order[:-1]]).any(axis=1)))

  if all_finite and unique_marks.all():
    return None, None

  idxs_unique = np.where(unique_marks)[0]
  idxs_duplicate = np.where(~unique_marks)[0]

  unique_map = np.arange(x.shape[0])

  if not all_finite:
    invalid_point = np.argmin(finite_x)
    unique_map[~finite_x] = invalid_point
  else:
    invalid_point = -1

  unique_map[order[idxs_duplicate]] = order[idxs_unique[(idxs_unique.reshape(-1, 1) < idxs_duplicate.reshape(1, -1)).sum(axis=0) - 1]]

  unique_idxs = np.unique(unique_map)
  if invalid_point in unique_idxs:
    unique_idxs = unique_idxs[unique_idxs != invalid_point]

  return unique_map, unique_idxs

def _pca(x, threshold):
  x_mean = np.mean(x, axis=0).reshape(1, -1)
  x_gain = np.std(x, axis=0)
  x_gain[x_gain <= np.finfo(float).eps] = 0.
  x_gain[x_gain != 0.] = 1. / x_gain[x_gain != 0.]
  xtx = (np.dot(x.T, x) / x.shape[0] - (x_mean.T * x_mean)) * x_gain.reshape(-1, 1) * x_gain.reshape(1, -1)
  eigval, eigvec = np.linalg.eigh(xtx)

  eigsum_threshold = eigval.sum() * threshold
  axes = []
  for axis in np.argsort(eigval)[::-1].tolist():
    axes.append(axis)
    if eigval[axes].sum() >= eigsum_threshold:
      break

  return np.dot(x, eigvec[:, axes])

def _do_adaptive_split(x, y, max_test_size, max_curvature=0.3, train_neighbors_ratio=0.3, max_n_points=10000, dry_run=False):
  # max_curvature in [0, 1] - the maximum curvature of the landscape region which allows to use its center point as the test point, recommended 0.3-0.6.
  #                           Increase max_curvature value to weaken the "flatness" requirement for landscape regions and increase the number of test points.
  # train_neighbors_ratio in [0, 1] - defines for each test point the ratio of neighboring points that should belong to train sample, recommended 0.2-0.5.
  #                                    It prevents the critical decrease of train points density in "flatter" landscape regions. The more its value is,
  #                                    the more surrounding training points we require for each test point - hence the less train points we have.
  #                                    When it is set to 0 we can use a candidate point for the test if there is at least one neighboring train point.
  #                                    In contrast, 1 value means that all the neighboring points of each test point should be kept in training sample.
  train_indices = np.ones((x.shape[0],), dtype=bool)

  if x.shape[0] > max_n_points:
    n_blocks = (x.shape[0] + max_n_points // 2) // max_n_points + 1
    _, labels = _init_clusters_center(x, n_blocks)
    unique_labels = np.unique(labels)
    if unique_labels.size == 1:
      # The data looks like a single point so let's toss the coin and assign all points either to train or test.
      train_indices[:] = np.random.random() >= 0.5
      return train_indices

    for label in unique_labels:
      idxs = (labels == label)
      train_indices[idxs] = _do_adaptive_split(x[idxs], y[idxs], max_test_size=max_test_size, max_curvature=max_curvature,
                                               train_neighbors_ratio=train_neighbors_ratio, max_n_points=max_n_points,
                                               dry_run=dry_run)
    return train_indices

  fronts = _generate_fronts(x=x, n_fronts=min((100 if dry_run else 10000), x.size))

  valid_y = np.isfinite(y).all(axis=1)
  if not valid_y.any():
    y = np.zeros(y.shape)
  elif not valid_y.all():
    y = y.copy()
    y[~valid_y] = np.percentile(y[valid_y], 50., axis=0).reshape(1, -1)

  route = _MultiRoute(x, y, w=None, fronts=fronts)

  # Calculate curvature level of the resulting fronts consisting of training points
  dydx2 = np.fabs(np.diff(route.dydx, axis=1)).reshape(len(fronts), -1)
  np.divide(dydx2, np.clip(np.max(np.fabs(route.dydx), axis=1), 1, np.inf), out=dydx2)
  dydx2 = dydx2.mean(axis=1)

  # Select "flat" fronts with low curvature level
  def get_flat_fronts(curvature_threshold):
    flat_fronts_idx = []
    flat_fronts_score = []

    for i in np.where(dydx2 <= curvature_threshold)[0]:
      # Find all fronts which are crossing the current "flat" front at the center point (w.r.t duplicated points)
      # Choose the current "flat" front if mean curvature value of the found fronts is not that large
      score = dydx2[route.fronts[:, 1] == route.fronts[i, 1]].mean()
      if score <= 2 * curvature_threshold:
        flat_fronts_idx.append(i)
        flat_fronts_score.append(score)

    return np.asarray(flat_fronts_idx, dtype=int), flat_fronts_score

  flat_fronts_idx, flat_fronts_score = get_flat_fronts(max_curvature)

  # Test variance if centers of all flat fronts are set to the test sample
  test_candidate_idx, test_candidate_counts = _unique_and_counts(route.fronts[flat_fronts_idx][:, 1])

  # Ensure training sample split
  while len(flat_fronts_idx) < 0.1 * x.shape[0] or not _test_split_variance(y, y[test_candidate_idx]):
    max_curvature += 0.05
    flat_fronts_idx, flat_fronts_score = get_flat_fronts(max_curvature)
    test_candidate_idx, test_candidate_counts = _unique_and_counts(route.fronts[flat_fronts_idx][:, 1])
    if max_curvature > 0.8:
      break

  # Sort "flat" fronts according to the mean curvature level of all the fronts crossing the center points
  flat_fronts = route.fronts[flat_fronts_idx][np.argsort(flat_fronts_score)]

  neighbor_count = np.zeros((x.shape[0],), dtype=int)
  neighbor_count[test_candidate_idx] += test_candidate_counts

  test_point_indices = []
  aligned_variances = False
  aligned_test_set_size = 0

  # Scale the required number of train neighbors for each test point depending on the dimensionality.
  # For larger dimensions we need more surrounding training points.
  train_neighbors_ratio = train_neighbors_ratio ** (1. / x.shape[1])

  sample_stat = _SplittingStat(y, train_indices)

  # We can not use the central points of all the fronts as test points,
  # since it may lead to gaps in regions with highly connected flat fronts.
  # Use a central point as a test only if its connected to train points within fronts.
  while len(flat_fronts) and max_test_size > 0:
    max_test_size -= 1

    if len(test_point_indices) < 3 or aligned_variances:
      # Points of "flatter" fronts are preferred,
      # so we start from the beginning of sorted front's array.
      new_test_point = flat_fronts[0, 1]
    else:
      # Select points that align variances of the test and whole samples,
      # since the whole sample will be eventually used to train a final model
      sample_stat.select_best(flat_fronts[sorted(np.unique(flat_fronts[:, 1], return_index=True)[1]), 1])
      # if we've failed to select the best point then select the flat one
      new_test_point = sample_stat.best_index if sample_stat.best_index >= 0 else flat_fronts[0, 1]

    test_point_indices.append(new_test_point)
    train_indices[new_test_point] = False

    aligned_variances = sample_stat.commit(new_test_point)
    if aligned_variances:
      aligned_test_set_size = len(test_point_indices)

    # Filter out fronts centered at the new test point
    exclude_mask = flat_fronts[:, 1] == test_point_indices[-1]
    # Filter out only fronts with test points on both sides, the rest will be checked with train_neighbors_ratio
    exclude_mask += ~(train_indices[flat_fronts[:, 0]] + train_indices[flat_fronts[:, 2]])

    flat_fronts = flat_fronts[~exclude_mask]
    # Filter out candidate test points that have not enough neighboring training points
    if 0 < train_neighbors_ratio <= 1 and not dry_run:
      remove_candidate_idx, remove_candidate_counts = _unique_and_counts(flat_fronts[:, 1])
      remove_candidate_idx = remove_candidate_idx[np.less(remove_candidate_counts, train_neighbors_ratio * neighbor_count[remove_candidate_idx])]
      if remove_candidate_idx.size:
        flat_fronts = flat_fronts[~(flat_fronts[:, 1].reshape(-1, 1) == remove_candidate_idx[np.newaxis]).any(axis=1)]

  if aligned_test_set_size:
    train_indices.fill(True)
    test_point_indices = test_point_indices[:aligned_test_set_size]
    train_indices[test_point_indices] = False

  return train_indices

class _SplittingStat(object):
  def __init__(self, y, train_indices, alpha=0.1):
    self.eps = np.finfo(float).eps**0.5
    self.y, self.y_var = y, np.clip(np.var(y, axis=0, ddof=1), self.eps, np.inf)
    self.best_index, self.best_diff, self.best_f_test = -1, np.inf, False

    y_train = y if train_indices.all() else y[train_indices]
    self.train_n = len(y_train)
    self.train_mean=np.mean(y_train, axis=0)
    self.train_var=np.var(y_train, axis=0, ddof=1)
    del y_train

    if train_indices.all():
      self.test_n = 0
      self.test_mean = np.zeros_like(self.train_mean)
      self.test_var = np.zeros_like(self.train_var)
    else:
      y_test = y[~train_indices]
      self.test_n=len(y_test)
      self.test_mean=np.mean(y_test, axis=0)
      self.test_var=np.var(y_test, axis=0, ddof=1)
      del y_test

    self.alpha = alpha
    self._init_f_test()

  def _recalc(self, point_index):
    # calculate train/test mean and variance if we move point_index from train to test
    x = self.y[point_index]
    vector_x = x.ndim == 1
    if vector_x:
      x = x[np.newaxis]

    # remove point x from the train sample
    delta = self.train_mean[np.newaxis] - x
    train_mean = (self.train_mean[np.newaxis] + delta / float(self.train_n - 1)) if self.train_n > 1 else np.zeros_like(x)
    train_var = (self.train_var[np.newaxis] + (self.train_var[np.newaxis] + delta * (x - train_mean)) / float(self.train_n - 2)) if self.train_n > 2 else np.zeros_like(x)

    # add point x to the test sample
    if not self.test_n:
      test_mean, test_var = x, np.zeros_like(x)
    else:
      delta = x - self.test_mean[np.newaxis]
      test_mean = self.test_mean[np.newaxis] + delta / float(self.test_n + 1)
      test_var = self.test_var[np.newaxis] + (delta * (x - test_mean) - self.test_var[np.newaxis]) / self.test_n

    return (train_mean[0], train_var[0], test_mean[0], test_var[0]) \
      if vector_x else (train_mean, train_var, test_mean, test_var)

  def _init_f_test(self):
    # reinitialize statistics for F-test.

    if self.train_n > 2 and self.test_n > 0:
      # all following tests have the same F-statistics: ddof=1 for train and test,
      # but train has one point out while test have one point in
      F_distr = _fdist(self.train_n - 2, self.test_n)
      self.F_min = F_distr.quantile(0.5*self.alpha, complement=False)
      self.F_max = F_distr.quantile(0.5*self.alpha, complement=True)
    else:
      self.F_min, self.F_max = -np.inf, np.inf

  def commit(self, point_index):
    # update all statistics considering we move point_index from train to test set
    self.best_index, self.best_diff, self.best_f_test = -1, np.inf, False
    self.train_mean, self.train_var, self.test_mean, self.test_var = self._recalc(point_index)
    self.train_n -= 1
    self.test_n += 1
    self._init_f_test()
    return self.f_test()

  def select_best(self, candidates):
    _, all_train_var, _, all_test_var = self._recalc(candidates)
    all_diff = (np.fabs(all_train_var - all_test_var) / self.y_var.reshape(1, -1)).sum(axis=1)

    for point_index, train_var, test_var, curr_diff in zip(candidates, all_train_var, all_test_var, all_diff):
      if curr_diff < self.best_diff:
        self.best_index, self.best_diff = int(point_index), curr_diff
        F_stat = (train_var + self.eps) / (test_var + self.eps)
        self.best_f_test = np.greater_equal(F_stat, self.F_min).all() and np.less_equal(F_stat, self.F_max).all()
        if self.best_f_test:
          return True

    return False

  def f_test(self):
    if self.train_n < 2 or self.test_n < 2:
      return False
    F_distr = _fdist(self.train_n - 1, self.test_n - 1)
    F_min = F_distr.quantile(0.5*self.alpha, complement=False)
    F_max = F_distr.quantile(0.5*self.alpha, complement=True)
    F_stat = (self.train_var + self.eps) / (self.test_var + self.eps)
    return np.greater_equal(F_stat, F_min).all() and np.less_equal(F_stat, F_max).all()

def _adaptive_split(x, y, random_state=None, max_curvature=0.3, train_neighbors_ratio=0.3, max_n_points=10000, min_test_size=None, dry_run=False):
  if x is None or y is None:
    return np.empty((0,), dtype=_ctypes.c_bool)

  x, y = np.atleast_2d(x), np.atleast_2d(y)

  # Find duplicated points
  unique_map, unique_idxs = _map_duplicates(x)

  # Max test size is the difference between the number of unique points and min sample size (2d + 3)
  min_train_size = (2 * (x.shape[1] + y.shape[1]) + 1)
  max_test_size = (x.shape[0] if unique_idxs is None else len(unique_idxs)) - min_train_size
  max_test_size = max(max_test_size, int(min_test_size) if min_test_size else 0)
  if max_test_size <= 0:
    # (2d+3) restricts the minimal train and test samples size
    return np.ones((x.shape[0],), dtype=bool)

  rnd_state = np.random.get_state()
  try:
    if random_state is not None and not isinstance(random_state, string_types):
      np.random.set_state(random_state.get_state())

    if unique_idxs is None:
      return _do_adaptive_split(_pca(x, 0.95) if x.shape[1] > 1 else x, y, max_test_size, max_curvature=max_curvature,
                                     train_neighbors_ratio=train_neighbors_ratio, max_n_points=max_n_points, dry_run=dry_run)

    unique_train = _do_adaptive_split(_pca(x[unique_idxs], 0.95) if x.shape[1] > 1 else x[unique_idxs],
                                      _average_y_over_unique_x(unique_map, unique_idxs, y), max_test_size,
                                      max_curvature=max_curvature, train_neighbors_ratio=train_neighbors_ratio,
                                      max_n_points=max_n_points, dry_run=dry_run)
    return _convert_back_unique_train(unique_map, unique_idxs, unique_train)
  finally:
    np.random.set_state(rnd_state)

def _get_adaptive_tensor_subsample(x, y, unique_x, tensor_structure, max_curvature=0.3):
  unique_map, unique_idxs = _map_duplicates(x)
  if unique_map is None:
    return _get_adaptive_tensor_subsample_on_unique_x(x=x, y=y, unique_x=unique_x,
                                                      tensor_structure=tensor_structure,
                                                      max_curvature=max_curvature)

  clean_train_indices = _get_adaptive_tensor_subsample_on_unique_x(x=x[unique_idxs],
                                                                   y=_average_y_over_unique_x(unique_map, unique_idxs, y),
                                                                   unique_x=unique_x, tensor_structure=tensor_structure,
                                                                   max_curvature=max_curvature)
  return _convert_back_unique_train(unique_map, unique_idxs, clean_train_indices)


def _select_work_buffer_size(unique_map, unique_idxs):
  # avoid using more than 1G of memory
  min_blck_size = 256
  max_mem_use = 1024*1024*1024 // min_blck_size
  block_size_1 = min(unique_idxs.size, max(min_blck_size, max_mem_use//unique_map.size*min_blck_size))
  block_size_2 = min(unique_map.size, max(min_blck_size, max_mem_use//block_size_1*min_blck_size))
  return block_size_1, block_size_2

def _convert_back_unique_train(unique_map, unique_idxs, unique_train):
  block_size_1, block_size_2 = _select_work_buffer_size(unique_map, unique_idxs)

  unique_train = unique_idxs[unique_train].reshape(1, -1)

  train_points = np.zeros(unique_map.size, dtype=bool)
  for j_start in xrange(0, unique_map.size, block_size_2):
    j_stop = min(unique_map.size, j_start + block_size_2)
    train_points_j = train_points[j_start:j_stop]
    unique_map_j = unique_map[j_start:j_stop].reshape(-1, 1)
    for i_start in xrange(0, unique_train.shape[1], block_size_1):
      i_stop = min(unique_idxs.size, i_start + block_size_1)
      np.logical_or(train_points_j, np.equal(unique_train[:, i_start:i_stop], unique_map_j).any(axis=1), out=train_points_j)

  return train_points

def _average_y_over_unique_x(unique_map, unique_idxs, y):
  block_size_1, block_size_2 = _select_work_buffer_size(unique_map, unique_idxs)

  avg_y = y[unique_idxs] # use average y for duplicated points

  work = np.zeros((block_size_1, block_size_2), dtype=bool)
  work_sum = np.zeros(unique_map.size, dtype=int)
  for i_start in xrange(0, unique_idxs.size, block_size_1):
    i_stop = min(unique_idxs.size, i_start + block_size_1)
    work_i = work[:(i_stop - i_start)]
    work_sum_i = work_sum[:(i_stop - i_start)]
    work_sum_i.fill(0)

    for j_start in xrange(0, unique_map.size, block_size_2):
      j_stop = min(unique_map.size, j_start + block_size_2)
      work_ij = work_i[:, :(j_stop - j_start)]
      np.equal(unique_idxs[i_start:i_stop].reshape(-1, 1), unique_map[j_start:j_stop].reshape(1, -1), out=work_ij)
      work_sum_i += work_ij.sum(axis=1)

    for k in np.where(work_sum_i > 1)[0]:
      avg_y[i_start + k] = y[unique_map == unique_idxs[i_start + k]].mean(axis=0)

  return avg_y

def _get_adaptive_tensor_subsample_on_unique_x(x, y, unique_x, tensor_structure, max_curvature=0.3):
  subsample = np.ones((x.shape[0], ), dtype=bool)

  tensor_structure_levels = {}
  for tensor_dims, levels in zip(tensor_structure, unique_x):
    tensor_dims = tuple(tensor_dims[:-1] if isinstance(tensor_dims[-1], string_types) else tensor_dims)
    tensor_structure_levels[tensor_dims] = _shared.as_matrix(levels, shape=(None, len(tensor_dims)))

  candidate_levels_score = {}
  neighboring_levels_id = {}
  excluded_levels_id = {}

  def filter_out_neighboring_levels(tensor_dims, candidate_levels_id, filtered_levels_id=None):
    filtered_levels_id = [] if filtered_levels_id is None else filtered_levels_id[:]

    for level in candidate_levels_id:
      if level not in filtered_levels_id and \
         neighboring_levels_id[tensor_dims][level][0] not in filtered_levels_id and \
         neighboring_levels_id[tensor_dims][level][1] not in filtered_levels_id:
        filtered_levels_id.append(level)

    # This is suitable for small high-dimensional tensor samples
    max_levels_numbers = max(1, int(0.1 * len(tensor_structure_levels[tensor_dims])))
    if len(filtered_levels_id) > max_levels_numbers:
      filtered_levels_id = filtered_levels_id[:max_levels_numbers]

    return filtered_levels_id

  def mark_excluded_levels(tensor_dims, excluded_levels):
    if len(excluded_levels):
      # Slice only marked points
      x_variable_slice = x[:, tensor_dims][subsample]
      mask = np.ones((x_variable_slice.shape[0],), dtype=bool)
      for level in excluded_levels:
        mask[(x_variable_slice == level).all(axis=1)] = False
      subsample[subsample] = mask

  for tensor_dims, levels in iteritems(tensor_structure_levels):
    neighboring_levels_id[tensor_dims] = np.zeros((levels.shape[0], 2), int)
    candidate_levels_score[tensor_dims] = {'max': np.ones(levels.shape[0]) * np.inf, 'mean+std': np.ones(levels.shape[0]) * np.inf}

    if 3 > levels.shape[0]:
      continue

    for i, level in enumerate(levels):
      # for 1D factor boundary points should remain in training set
      if 1 == levels.shape[1] and i in [0, levels.shape[0] - 1]:
        continue

      # Find indices of points with the current value of factor
      idx = np.argwhere((x[:, tensor_dims] == level).all(axis=1)).ravel()
      # Find their neighboring points
      if 1 == levels.shape[1]:
        neighboring_levels_id[tensor_dims][i] = (i - 1, i + 1)
      else:
        distances = np.hypot.reduce(level - levels, axis=1)
        distances[i] = np.inf
        distance_sorted_ids = np.argsort(distances)
        neighboring_levels_id[tensor_dims][i] = (distance_sorted_ids[0], distance_sorted_ids[1])
      idx0 = np.argwhere((x[:, tensor_dims] == levels[neighboring_levels_id[tensor_dims][i][0]]).all(axis=1)).ravel()
      idx1 = np.argwhere((x[:, tensor_dims] == levels[neighboring_levels_id[tensor_dims][i][1]]).all(axis=1)).ravel()

      # Sort points to map them along the factor
      fronts = np.vstack([idx0[np.lexsort(x[idx0].T)], idx[np.lexsort(x[idx].T)], idx1[np.lexsort(x[idx1].T)]]).T
      route = _MultiRoute(x, y, w=None, fronts=fronts)
      # Calculate curvature level of the resulting fronts consisting of training points
      curvature = np.abs(np.diff(route.dydx, axis=1)).flatten()
      np.divide(curvature, np.clip(np.max(np.abs(route.dydx), axis=1).flatten(), 1, np.inf), out=curvature)

      if curvature.size:
        candidate_levels_score[tensor_dims]['max'][i] = np.max(curvature)
        candidate_levels_score[tensor_dims]['mean+std'][i] = np.mean(curvature) + np.std(curvature)

    candidate_levels_id = [i for i, curvature in enumerate(candidate_levels_score[tensor_dims]['max']) if curvature < max_curvature]
    candidate_levels_id.sort(key=lambda i: candidate_levels_score[tensor_dims]['max'][i])
    excluded_levels_id[tensor_dims] = filter_out_neighboring_levels(tensor_dims, candidate_levels_id)
    mark_excluded_levels(tensor_dims, levels[excluded_levels_id[tensor_dims]])

  # Try to exclude some additional points under the weakened constraints
  # if only one dimension was considered or the test sample is too small.
  n_excluded_dims = sum([bool(levels) for _, levels in iteritems(excluded_levels_id)])
  while (n_excluded_dims < 2 or np.sum(~subsample) < 0.1 * x.shape[0]) and max_curvature < 0.8:
    for tensor_dims, levels in iteritems(tensor_structure_levels):
      if 3 > levels.shape[0] or len(excluded_levels_id[tensor_dims]):
        continue
      # Also add penalty for high-dimensional tensor structures to restrict maximal allowed score value.
      # The more tensor dimensions we have the more is the cost of level exclusion.
      candidate_levels_id = [i for i, curvature in enumerate(candidate_levels_score[tensor_dims]['mean+std']) if curvature < max_curvature / (len(tensor_structure) - 1)]
      candidate_levels_id.sort(key=lambda i: candidate_levels_score[tensor_dims]['mean+std'][i])
      excluded_levels_id[tensor_dims] = filter_out_neighboring_levels(tensor_dims, candidate_levels_id)
      mark_excluded_levels(tensor_dims, levels[excluded_levels_id[tensor_dims]])
      if excluded_levels_id[tensor_dims]:
        n_excluded_dims = sum([bool(levels) for _, levels in iteritems(excluded_levels_id)])
    max_curvature += 0.05

  if np.all(subsample):
    min_score = np.inf
    min_score_dims = ()
    min_score_levels = []
    for tensor_dims, levels in iteritems(tensor_structure_levels):
      candidate_id = np.argmin(candidate_levels_score[tensor_dims]['mean+std'])
      candidate_score = candidate_levels_score[tensor_dims]['mean+std'][candidate_id]
      if candidate_score < min_score:
        min_score = candidate_score
        min_score_dims = tensor_dims
        min_score_levels = [levels[candidate_id]]
    if min_score < np.inf:
      mark_excluded_levels(min_score_dims, min_score_levels)

  return subsample

def _merge_less_factors(tensor_structure, unique_x):
  cardinalities = [len(_) for _ in unique_x]
  factor_in, factor_out = np.argsort(cardinalities)[:2]

  tensor_structure[factor_in] += tensor_structure[factor_out]
  unique_x[factor_in] = np.hstack((np.tile(unique_x[factor_in], (cardinalities[factor_out], 1)), \
                                   np.repeat(unique_x[factor_out], cardinalities[factor_in], axis=0)))

  tensor_structure.pop(factor_out)
  unique_x.pop(factor_out)

  return tensor_structure, unique_x

def _calc_factor_sizes(train_test_ratio, min_factor_size, unique_x):
  factor_sizes = np.array([len(_) for _ in unique_x])
  rho = train_test_ratio**(1.0 / len(unique_x))
  factor_train_sizes = np.maximum(np.minimum(min_factor_size, factor_sizes), (factor_sizes * rho).astype(int))
  return factor_sizes, factor_train_sizes

def _get_new_factors(x, train_test_ratio, full_sample_size, min_factor_size, tensor_structure, fixed_structure):
  unique_x = []
  for factor in tensor_structure:
    if isinstance(factor[-1], string_types):
      factor = factor[:-1]
    unique_x.append(_get_unique_elements(x[:, factor], False))

  # update minimal factor size (may be all factors were less than min_factor_size so it's ok to keep it small)
  factor_sizes = np.array([len(_) for _ in unique_x], dtype=int)
  factor_sizes.sort()
  factor_sizes = factor_sizes[1 < factor_sizes]

  if len(factor_sizes):
    min_factor_size = min(min_factor_size, max(2, factor_sizes[-1] - 1))

  factor_sizes, factor_train_sizes = _calc_factor_sizes(train_test_ratio, min_factor_size, unique_x)

  # If there are duplicate points, make split using only unique points
  if np.prod(factor_sizes) < full_sample_size:
    full_sample_size = np.prod(factor_sizes)

  if np.prod(factor_train_sizes) == full_sample_size:
    if fixed_structure:
      raise _ex.InvalidProblemError('Factor sizes are too small to correctly split the data set into training and test samples!')
    else:
      # strip techniques if any
      tensor_structure = [(_[:-1] if isinstance(_[-1], string_types) else _) for _ in tensor_structure]

      while len(tensor_structure) > 1:
        tensor_structure, unique_x = _merge_less_factors(tensor_structure, unique_x)
        factor_sizes, factor_train_sizes = _calc_factor_sizes(train_test_ratio, min_factor_size, unique_x)
        if np.prod(factor_train_sizes) != full_sample_size:
          break

  factor_sizes_order = np.argsort(factor_sizes)
  target_sample_size = full_sample_size * train_test_ratio

  # increment factors starting from the less one (we should keep the less factors as large as possible)
  for factor_index in factor_sizes_order[::]:
    if np.prod(factor_train_sizes) >= target_sample_size:
      break
    if factor_train_sizes[factor_index] < factor_sizes[factor_index]:
      factor_train_sizes[factor_index] += 1

  # decrement factors starting from the largest one
  for factor_index in factor_sizes_order[-1::-1]:
    if np.prod(factor_train_sizes) <= target_sample_size:
      break
    if factor_train_sizes[factor_index] > min_factor_size:
      factor_train_sizes[factor_index] -= 1

  return factor_train_sizes, tensor_structure, unique_x

def _get_tensor_sample_subsample(x, unique_x, tensor_structure, factor_train_sizes, random_state):
  subsample = np.ones((x.shape[0], ), dtype=bool)

  for i, factor in enumerate(tensor_structure):
    if isinstance(factor[-1], string_types):
      factor = factor[:-1]

    n_sel = factor_train_sizes[i]
    n_points = len(unique_x[i])

    if n_sel == n_points:
      # there is nothing to remove
      continue

    x_sample = _shared.as_matrix(unique_x[i], shape=(None, len(factor)), name=("'unique_x[%d]' argument" % i))

    # for 1D factor boundary points should remain in training set
    if 1 < len(factor):
      points_in = np.where(_select_subsample(n_sel, x_sample, None, random_state))[0]
    elif 1 == n_points:
      points_in = [0,]
    else:
      points_in = [0, n_points - 1,]
      if 2 < n_sel:
        points_in.extend(np.where(_select_subsample(n_sel - 2, x_sample[1:-1], None, random_state))[0] + 1)

    points_out = [_ for _ in xrange(n_points) if _ not in points_in]

    # get only marked points
    x_factor = x[:, factor].reshape(-1, len(factor))
    x_factor = x_factor[subsample]
    markers = np.ones((x_factor.shape[0], ), dtype=bool)
    for point in unique_x[i][points_out]:
      markers[(x_factor == point).all(axis=1)] = False
    subsample[subsample] = markers

  return subsample

def _optional_split(data, options, accelerator_options):
  if data.get('x_test') is not None and data.get('y_test') is not None:
    return data

  train_test_ratio = accelerator_options.get('TrainingSubsampleRatio', 0.)
  if train_test_ratio < 0. or train_test_ratio >= 1.:
    data['x_test'], data['y_test'], data['w_test'] = None, None, None
    return data

  random_state = "cart" if _shared.parse_bool(options.get('GTApprox/Deterministic'))\
            else np.random.RandomState(int(options.get('GTApprox/Seed')))

  cartesian_structure = _shared.parse_json(options.get('GTApprox/TensorFactors'))
  fixed_structure = True
  if not cartesian_structure and options.get('GTApprox/Technique').lower() in ['ta', 'tgp', 'auto']:
    fixed_structure = False
    cartesian_structure = _shared.parse_json(options.get('//Service/CartesianStructure'))

  if cartesian_structure:
    initial_cartesian_factors = sorted([tuple(sorted(_[:-1])) if isinstance(_[-1], string_types) else tuple(sorted(_)) for _ in cartesian_structure])

    train_indices, test_indices, cartesian_structure = train_test_split(data['x'], data['y'], train_test_ratio,
                                                                        tensor_structure=cartesian_structure,
                                                                        fixed_structure=fixed_structure,
                                                                        random_state=random_state)

    new_cartesian_factors = sorted([tuple(sorted(_[:-1])) if isinstance(_[-1], string_types) else tuple(sorted(_)) for _ in cartesian_structure])
    if new_cartesian_factors != initial_cartesian_factors:
      options.set('GTApprox/TensorFactors')
      options.set('//Service/CartesianStructure', cartesian_structure)
  else:
    train_indices, test_indices, _ = train_test_split(data['x'], data['y'], train_test_ratio, random_state=random_state)

  data['x_test'] = data['x'][test_indices]
  data['y_test'] = data['y'][test_indices]

  if data.get('weights') is not None:
    data['w_test'] = data['weights'][test_indices]
    data['weights'] = data['weights'][train_indices]

  if data.get('tol') is not None:
    data['tol'] = data['tol'][train_indices]

  data['x'] = data['x'][train_indices]
  data['y'] = data['y'][train_indices]

  data['modified_dataset'] = True

  return data

def _unique_and_counts(ar):
  try:
    return np.unique(ar, return_counts=True)
  except:
    pass

  # workaround for old numpy
  ar = np.sort(ar, axis=None) # returns flattened array
  marks = np.ones(ar.shape[0]+1, dtype=bool) # add last mark for simplicity
  np.not_equal(ar[:-1], ar[1:], out=marks[1:-1])
  marks = np.where(marks)[0]

  return ar[marks[:-1]], marks[1:] - marks[:-1]
