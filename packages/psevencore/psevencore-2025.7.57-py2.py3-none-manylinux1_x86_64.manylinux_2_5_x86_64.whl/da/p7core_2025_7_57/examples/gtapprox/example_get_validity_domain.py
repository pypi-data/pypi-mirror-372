#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
pSeven Core for Python example: getting model validity domain.


This example demonstrates how you can check if new point belongs to model validity domain.

Exact definition of validity domain can be very different and depend on lots of things,
i.e. data, problem statement, model type and etc.

In the example by validity domain we mean the region, where you can trust model predictions.

When checking if you should trust model predictions at a given point, first of all you should check
whether you are operating in interpolation or extrapolation regime (as models often are unreliable outside the training data).
The easiest check you can do is to look whether considered point lies inside or outside borders of
the hypercube training sample was generated from.

It may allow to quickly find points that are far away from training sample and in which you
should not trust model predictions.

The other approach you can use for the points that are not far away from the training sample
is to construct classifier model that would tell in which points model would give accurate predictions.

Below we demonstrate implementation of both checks.

For the example we will use target function f(x_1, x_2):

f(x_1, x_2) = |2 + sin(4 * x_1 + 4 * x_2) + 0.5 * eps|,

where eps is a standard normal noise.
"""

#[0] required imports
import os
import matplotlib.pyplot as plt
import numpy as np

from da.p7core import gtapprox, loggers
#[0]


#[1] definition of the target function
def true_function(points, noise_variance=0.005):
  """ A simple noised function we will use to study approximation validity domain.
  """
  values = 2 + np.sin(np.sum(4 * points, axis=1, keepdims=True))
  values = values + noise_variance ** 0.5 * np.random.randn(np.shape(values)[0],
                                                            np.shape(values)[1])
  values = np.abs(values)
  return values
#[1]

#[2]
def get_data(sample_size=200, input_dimension=2):
  """ Get data randomly distributed in a unit hypercube
  """
  points = np.random.rand(sample_size, input_dimension)
  values = true_function(points)

  return points, values
#[2]

#[3]
def construct_classifier(points, values, predictions, relative_error_bound=0.1):
  """ Construct classifier that returns probability that model gives good prediction
  in considered point i.e. relative error is smaller than relative_error_bound
  """
  relative_errors = np.abs(values - predictions) / (np.abs(values) + 1e-9)
  # 1e-9 is added here to ensure that no problem occur in cases true value = 0

  # Construct classifier
  builder = gtapprox.Builder()
  builder.set_logger(loggers.StreamLogger())
  validity_classifier = builder.build(points, relative_errors < relative_error_bound,
                                      options={'gtapprox/technique': 'gbrt',
                                               '/GTApprox/GBRTObjective': 'binary:logistic'})

  return validity_classifier
#[3]

#[4]
def calculate_auc(x_axis_values, y_axis_values):
  """ Get area under curve
  x axis values are sorted in ascending order
  """
  return np.trapz(y_axis_values, x_axis_values)
#[4]

#[5]
def get_fp_tp_curve(y_true, y_score):
  """ Get False Positive and True Positive values for various thresholds
  """
  # Ravel data
  y_true = y_true.ravel()
  y_score = y_score.ravel()

  # Sort scores and corresponding truth values
  descending_sort_indices = np.argsort(y_score)[::-1]
  y_score = y_score[descending_sort_indices]
  y_true = y_true[descending_sort_indices]

  # Use only distinct scores
  distinct_value_indices = np.where(-np.diff(y_score) > 1e-7)[0]
  threshold_indexes = np.r_[distinct_value_indices, len(y_true) - 1]

  # Get true positive and false positive number
  true_positive_number = (0. + y_true).cumsum()[threshold_indexes]
  false_positive_number = (1. - y_true).cumsum()[threshold_indexes]

  return false_positive_number, true_positive_number
#[5]

#[6]
def roc_curve(y_true, y_score):
  """ Get True Positive Rates and False Positive Rates for ROC curve construction
  """
  positive_number = np.sum(y_true)
  negative_number = np.sum(y_true == 0)

  false_positive_number, true_positive_number = get_fp_tp_curve(y_true, y_score)

  # add first line
  if false_positive_number[0] != 0:
    true_positive_number = np.r_[0, true_positive_number]
    false_positive_number = np.r_[0, false_positive_number]

  if negative_number > 0:
    false_positive_ratio = false_positive_number / negative_number
  else:
    false_positive_ratio = np.nan * false_positive_number

  if positive_number > 0:
    true_positive_ratio = true_positive_number / positive_number
  else:
    true_positive_ratio = np.nan * true_positive_number

  return false_positive_ratio, true_positive_ratio
#[6]

#[7]
def get_roc_curve(test_values, test_sim_probabilities):
  """ Get data for ROC curve
  """
  first_axis_rate, second_axis_rate = roc_curve(test_values, test_sim_probabilities)
  auc_value = calculate_auc(first_axis_rate, second_axis_rate)
  return first_axis_rate, second_axis_rate, auc_value
#[7]

#[8]
def get_confusion_matrix_label(negative_number, positive_number, first_quantile, second_quantile, max_len):
  false_positive = int(negative_number * first_quantile)
  true_negative = negative_number - false_positive
  true_positive = int(positive_number * second_quantile)
  false_negative = positive_number - true_positive

  false_positive_string = str(false_positive)
  true_negative_string = str(true_negative)
  true_positive_string = str(true_positive)
  false_negative_string = str(false_negative)
  confusion_matrix_strings = [true_positive_string, false_negative_string,
                              false_positive_string, true_negative_string]

  confusion_matrix_strings = [x + ' ' * (max_len - len(x)) for x in confusion_matrix_strings]
  confusion_matrix_names = ['TP: ', 'FN: ', 'FP: ', 'TN: ']
  return ''.join(z + t for z, t in zip(confusion_matrix_names, confusion_matrix_strings))
#[8]

#[9]
def plot_roc_curve(test_values, test_sim_probabilities, quantile_list=[5, 25, 50, 75, 95]):
  """
    Plot Receiver operating characteristic (ROC) performance curve
    Inputs:
      test_values - numpy array of true values, 0 or 1
      test_sim_probabilities - numpy array of simulated probabilities with values inside the interval [0, 1]
      quantile_list - list of quantiles for which we display confusion matrices
    Outputs:
      auc_value - AUC value for classifier
      first_axis_rate - value for the first axis
      second_axis_rate - value for the second axis
  """
  # Get data for ROC curve
  first_axis_rate, second_axis_rate, auc_value = get_roc_curve(test_values, test_sim_probabilities)

  plt.figure()

  # Plot bisector of quadrant
  plt.plot([0, 1], [0, 1], "k--")

  # Plot rates
  plt.plot(first_axis_rate, second_axis_rate, label="ROC curve", linewidth=3)

  # Plot quantile points
  sample_size = len(test_values)
  positive_number = int(np.sum(test_values))
  negative_number = int(sample_size - np.sum(test_values))
  max_len = len(str(int(sample_size)))
  for quantile in quantile_list:
    first_quantile = np.percentile(first_axis_rate, quantile)
    second_quantile = np.percentile(second_axis_rate, quantile)

    label = get_confusion_matrix_label(negative_number, positive_number, first_quantile, second_quantile, max_len)
    plt.plot(first_quantile, second_quantile, 'o', label=label, markersize=15)

  # Set correct axis
  plt.axis([0.0, 1.0, 0.0, 1.0001])
  plt.grid(True)

  # Plot legend and labels
  plt.xlabel("False Positive Rate", fontsize=16)
  plt.ylabel("True Positive Rate", fontsize=16)
  plt.legend(loc="lower right", prop={"family" : "monospace"})
  plt.title("ROC AUC=%0.2f" % (auc_value))

  # Save file
  file_name = "roc_curve.png"
  plt.savefig(file_name)
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

  return first_axis_rate, second_axis_rate, auc_value
#[9]

#[10-0]
def main():
  """
  Main function builds approximation model, model for accuracy and
  draws corresponding ROC curve
  """

  #[10-1] Set what relative error we consider as bad
  """
  Here we set relative error bound on acceptable accuracy.
  """
  relative_error_bound = 0.1

  #[10-2] Get train and test data
  """
  Here we generate train and test data.
  """
  training_points, training_values = get_data(300)
  test_points, test_values = get_data(10000)

  #[10-3] Construct model and get error estimates (to train classifier with)
  """
  Here we construct approximation model.

  Note that we turn on internal validation to get the information on model accuracy.
  And we save internal validation predictions and get them from model to use them
  for constructing accuracy model.
  """
  print("Building initial surrogate model...\n")
  builder = gtapprox.Builder()
  builder.set_logger(loggers.StreamLogger())
  model = builder.build(training_points, training_values,
                        options={'GTApprox/Technique': 'GP',
                                 'GTApprox/InternalValidation': 'on',
                                 'GTApprox/IVSavePredictions': 'on',
                                 'GTApprox/IVSubsetCount': 10,
                                 'GTApprox/IVTrainingCount': 10,
                                })

  print("Done.\n")

  internal_validation_inputs = model.iv_info['Dataset']['Validation Input']
  internal_validation_outputs = model.iv_info['Dataset']['Validation Output']
  internal_validation_predictions = model.iv_info['Dataset']['Predicted Output']

  #[10-4] Construct classifier to get model accuracy estimate
  """
  Here we construct classifier that predicts model accuracy
  """
  print("Constructing classifier that tells if prediction in point would be accurate...")
  validity_classifier = construct_classifier(internal_validation_inputs,
                                             internal_validation_outputs,
                                             internal_validation_predictions,
                                             relative_error_bound)
  print("Done.\n")

  #[10-5] Check if test data lie inside hypercube formed by train data
  """
  Here we take data on training sample properties and check if test set points lie inside
  """

  print("Checking if points lie inside input domain...\n")
  points_lie_inside = np.ones(test_values.shape, dtype=np.bool_)

  input_sample_stats = model.details['Training Dataset']['Sample Statistics']['Input']

  for dimension in range(len(input_sample_stats['Count'])):
    check_dimension = (input_sample_stats['Min'][dimension] <=
                       test_points[:, dimension:dimension+1])
    check_dimension *= (test_points[:, dimension:dimension+1] <=
                        input_sample_stats['Max'][dimension])
    points_lie_inside = np.logical_and(points_lie_inside, check_dimension)
  print("Result:")
  print("%s points lie inside train sample area" % np.sum(points_lie_inside == True))
  print("%s points lie outside train sample area\n" % np.sum(points_lie_inside == False))


  #[10-6] Apply model and validity classifier for test data to check it's quality
  """
  Prepare test data predictions and true labels.
  """
  print("Using classifier to check accuracy in points...\n")
  sim_values = model.calc(test_points)
  valid_model_probability = validity_classifier.calc(test_points)

  sim_values_validity = np.abs((test_values - sim_values) / test_values)

  #[10-7] Plot result ROC curve
  """
  Draw ROC curve.
  """
  plot_roc_curve(sim_values_validity < relative_error_bound, valid_model_probability)
#[10-8]

if __name__ == "__main__":
  main()
