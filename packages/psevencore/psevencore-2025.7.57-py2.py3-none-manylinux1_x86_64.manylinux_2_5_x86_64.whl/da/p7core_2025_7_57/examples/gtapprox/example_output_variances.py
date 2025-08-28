#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
pSeven Core for Python example: usage of provided output variances.

This example demonstrates that usage of additional information allows us
to obtain better approximation and accuracy evaluation quality.
In particular we consider the case of provided output variances
for some points from the training sample

The example describes how output variances can be used during approximation construction.
We consider the problem of a target function approximation construction
for a given training sample of the target function values.
We also demonstrate that one can provide not all but only a part of all output variances.
We do this with replacing some variances by NaNs.

The workflow of the example is described below.
The example generates sample of function values noised in a nonuniform way
i.e. noise variance depends on the point location.
Then we estimate output variances for each point in the sample and
run GTApprox with and without provided estimations of noise variances.
For some points we replace output variances by NaNs so we emulate the case
when output variances are provided only for some subsample of the whole training sample.
Validation of obtained GTApprox models uses a separate test sample.

Model benefits from usage of output variances
in both terms of RRMS for approximation and accuracy evaluation.
We demonstrate difference of obtained models using 2D plots for
approximations and the target function, accuracy evaluation and actual approximation errors.
"""

#[0] required imports
import os

import matplotlib.pyplot as plt
import numpy as np

from da.p7core import gtapprox, gtdoe
#[0]

#[1] true function
def target_function(x, shift=0.7, scale=4.5):
  """
  Target function with 1D input.

  Args:
    x: 1D point or a NumPy array.
    shift, scale: the target function optional parameters

  Returns:
    Single function value or an array of values. Array shape is the same
    as input shape.
  """
  x_tilde = (x - shift) * scale
  result = np.sin(x_tilde) * np.exp(-x_tilde ** 2)
  return result
#[1]

# training sample generation
def generate_training_sample(points_number, point_evaluation_number, bounds=(0.0, 1.0)):
  """
  Generates sample with specified number of input points, number of noisy function evaluations at the point
  in a specified 1D design region.

  Args:
    points_number: number of points to generate, positive integer.
    point_evaluation_number: number of noisy function evaluations at each point, positive integer.
    bounds: bounds of the design region, tuple of two positive integers.

  Returns:
    List of points generated using GT DoE and
    list of lists of noised function values,
    each element from the top-level list is a list of noised function values at the corresponding point.
  """
  #[4] create generator
  generator = gtdoe.Generator()

  # set DoE options
  options = {"GTDoE/Technique": "LHS",
             "GTDoE/Deterministic": "yes",
             "GTDoE/Seed" : 200}
  generator.options.set(options)

  # generate points using GT DoE
  points = generator.generate(bounds=bounds,
                              count=points_number).points.reshape(-1, 1)
  #[4]

  #[5] generate noised values
  values = []
  for point in points:
    # get noise variance for the point
    point_noise_variance = 10e-4 + 0.2 * point * (point > 0.3)
    # generate noised function values
    values.append(target_function(point) +
                  point_noise_variance ** 0.5 *
                  np.random.randn(point_evaluation_number, 1))
  #[5]
  return points, values


#[6]
def estimate_noise_variances(training_values):
  """
  Estimate noise variances and mean at each input point.
  Mean estimation is straightforward.
  We use unbiased variance estimation with assumption about zero mean for noise values.
  We begin with variance estimation for provided values at each point.
  Then we obtain variance estimation for mean of provided values at each point.

  Args:
    training_values: training outputs, NumPy array.

  Returns:
    NumPy array of function values estimation and corresponding noise variances estimation at each point.
  """

  training_mean_values = []
  training_output_variance_values = []
  for point_values in training_values:
    training_mean_values.append(np.mean(point_values))
    training_value_variance_estimation = (np.sum((point_values - np.mean(point_values)) ** 2) /
                                          (point_values.shape[0] - 1))
    training_mean_value_variance_estimation = (training_value_variance_estimation /
                                               point_values.shape[0])
    training_output_variance_values.append(training_mean_value_variance_estimation)
  return training_mean_values, training_output_variance_values
#[6]

#[7]
def mix_in_nans(values, nan_points_number):
  """
  Replace values in random points with NaNs
  Using this script we emulate unavailability
  of provided output variances for some training points

  Args:
    values: initial input sample
    nan_points_number: number of points to replace with NaNs

  Return values with nans inserted
  """
  points_number = np.shape(values)[0]

  permuted_indexes = np.random.permutation(list(range(points_number)))

  nan_indexes = permuted_indexes[:nan_points_number]
  for index in nan_indexes:
    values[index] = np.nan
  return values
#[7]

#[8]
def build_models(training_points, training_values, training_output_variance_values):
  """
  Build models for the given training sample with and without output variances provided

  Args:
    training_points: training inputs, NumPy array.
    training_values: training outputs, NumPy array.
    training_output_variance_values: training output variances, NumPy array.

  Returns:
    Models obtained with and without usage of output variances
  """
  builder = gtapprox.Builder()
  builder.options.set({"GTApprox/Technique" : "GP",
                       "GTApprox/AccuracyEvaluation" : "on"})
  model = builder.build(training_points, training_values)
  model_with_output_variances = builder.build(training_points, training_values, outputNoiseVariance=training_output_variance_values)
  return model, model_with_output_variances
#[8]

#[9]
def validate_models(models, test_sample):
  """
  Validate constructed models using a test sample.
  We calculate RRMS errors and correlation between the true residuals and accuracy evaluation

  Args:
    models: two models constructed with GT approximation.
    test_sample: test points and corresponding test values.
  """
  model, model_with_output_variances = models
  test_points, test_values = test_sample

  print("Validating of model without usage of output variances")
  validation_result_model = model.validate(*test_sample)
  print("Validating of model with usage of output variances")
  validation_result_model_with_output_variances = model_with_output_variances.validate(*test_sample)
  print("Get approximation and accuracy evaluation for model without usage of output variances")
  model_values = model.calc(test_points)
  model_ae = model.calc_ae(test_points)
  print("Get approximation and accuracy evaluation for model with usage of output variances")
  model_with_output_variances_values = model_with_output_variances.calc(test_points)
  model_with_output_variances_ae = model_with_output_variances.calc_ae(test_points)
  ae_correlation = np.corrcoef(np.abs(model_values - test_values),
                                  model_ae, rowvar=0)[0, 1]
  ae_with_output_variances_correlation = np.corrcoef(np.abs(model_with_output_variances_values - test_values),
                                              model_with_output_variances_ae, rowvar=0)[0, 1]

  print("\tModel without usage of output variances RRMS: %s" % validation_result_model["RRMS"][0])
  print("\tModel with usage of output variances RRMS: %s" % validation_result_model_with_output_variances["RRMS"][0])
  print("\tAE for model without usage of output variances correlation: %s" % ae_correlation)
  print("\tAE for model with usage of output variances correlation: %s" % ae_with_output_variances_correlation)
#[9]

#[10]
def plot(models, samples):
  """
  Show and save example plots.

  Args:
    models: GTApprox models trained with and without usage of output variances,
    samples: training and test samples.

  Creates two figures: the first one is a plot with two subplots that depicts approximation
  obtained using models with and without usage of output variances,
  the second one is a plot with two subplots that depicts accuracy evaluation and actual errors
  for models with and without usage of output variances

  Figures are saved to the script working directory.
  """
  model, model_with_output_variances = models
  training_points, training_mean_values, training_variance_values, test_points, test_values = samples

  print("Generating plot data. Please wait...")
  # calculate values estimation
  test_values_sim = model.calc(test_points)
  test_values_sim_output_variances_used = model_with_output_variances.calc(test_points)
  # calculate accuracy evaluation
  test_values_sim_ae = model.calc_ae(test_points)
  test_values_sim_output_variances_used_ae = model_with_output_variances.calc_ae(test_points)

  # plot results options
  approximation_linewidth = 2.5
  ae_linewidth = 1.5

  # plot obtained approximations
  approximation_figure = plt.figure(figsize = (18, 8))
  approximation_figure.suptitle('Output variances: Approximation results', fontsize = 18)

  ax = approximation_figure.add_subplot(121)
  ax.set_xlabel("Points", fontsize ="18")
  ax.set_ylabel("Values", fontsize ="18")
  ax.set_title("We don't use output variances estimation", fontsize ="18")

  target_function_plot, = plt.plot(test_points, test_values, linewidth=approximation_linewidth - 0.5)
  model_plot, = plt.plot(test_points, test_values_sim, "-.g", linewidth=2 * approximation_linewidth)
  model_ae_plot, = plt.plot(test_points, test_values_sim - test_values_sim_ae, ":g", linewidth=ae_linewidth)
  plt.plot(test_points, test_values_sim + test_values_sim_ae, ":g", linewidth=ae_linewidth)

  training_sample_plot = plt.errorbar(training_points,
    training_mean_values,
    yerr = model.calc_ae(training_points).reshape(-1, ), fmt="bs")


  plt.legend([target_function_plot, training_sample_plot,
              model_plot, model_ae_plot],
            ["True function", "Training points",
             "Model", "Model $\\!\\pm\\!$ AE"], loc=2)

  ax = approximation_figure.add_subplot(122)
  ax.set_xlabel("Points", fontsize ="18")
  ax.set_ylabel("Values", fontsize ="18")
  ax.set_title("We use output variances estimation", fontsize ="18")

  target_function_plot, = plt.plot(test_points, test_values, linewidth=approximation_linewidth - 0.5)

  model_with_output_var_plot, = plt.plot(test_points, test_values_sim_output_variances_used,
                                         "--r", linewidth=approximation_linewidth)
  model_with_output_var_ae_plot, = plt.plot(test_points, test_values_sim_output_variances_used - test_values_sim_output_variances_used_ae,
                                            ":r", linewidth=ae_linewidth)
  plt.plot(test_points, test_values_sim_output_variances_used + test_values_sim_output_variances_used_ae,
           ":r", linewidth=ae_linewidth)

  training_sample_plot = plt.errorbar(training_points, training_mean_values,
                                      yerr = model_with_output_variances.calc_ae(training_points).reshape(-1, ), fmt="bs")

  plt.legend([target_function_plot, training_sample_plot,
              model_with_output_var_plot, model_with_output_var_ae_plot],
            ["Target function", "Training points",
             "Model, output variances used", "Model $\\!\\pm\\!$ AE, output variances used"], loc=2)

  # plot figures with actual errors and accuracy evaluations
  ae_figure = plt.figure(figsize = (18, 8))
  ae_figure.suptitle('Output variances: AE results', fontsize = 18)

  ax = ae_figure.add_subplot(121)
  diff_plot, = plt.plot(test_points, np.abs(test_values - test_values_sim),
                        linewidth=approximation_linewidth - 0.5)
  ae_plot, = plt.plot(test_points, test_values_sim_ae, ":g", linewidth=ae_linewidth)


  plt.legend([diff_plot, ae_plot],
            ["True errors", "AE"], loc=2)
  ax.set_xlabel("Points", fontsize ="18")
  ax.set_ylabel("Errors", fontsize ="18")
  ax.set_title("We don't use output variances estimation", fontsize ="18")

  ax = ae_figure.add_subplot(122)
  diff_plot, = plt.plot(test_points, np.abs(test_values - test_values_sim_output_variances_used),
                        linewidth=approximation_linewidth - 0.5)
  ae_plot, = plt.plot(test_points, test_values_sim_output_variances_used_ae,
                      ":r", linewidth=ae_linewidth)

  plt.legend([diff_plot, ae_plot],
            ["True errors if output variances used", "AE if output variances used"], loc=2)
  ax.set_xlabel("Points", fontsize ="18")
  ax.set_ylabel("Errors", fontsize ="18")
  ax.set_title("We use output variances estimation", fontsize ="18")

  # save and show plots
  title = "output_variances_example"
  approximation_figure.savefig(title)
  ae_title = "output_variances_example_ae"
  ae_figure.savefig(ae_title)
  print("Plot is saved to %s.png" % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    print("Close plot windows to finish.")
    plt.show()
#[10]

#[11]
def main():
  """
  Main example workflow:

  1. Set options for a training sample generation.
  2. Generate the training sample.
  3. Estimate output variances and mean outputs for the generated training sample.
  4. Mix in NaN values into output variances estimation
  5. Train models using the obtained sample with and without usage of estimated output variances.
  6. Generate a test sample and validate the models, get RRMS errors and correlations.
  7. Plot original function and approximations using constructed models, actual errors and accuracy evaluation.
  """
  np.random.seed(500)

  print("\npSeven Core for Python example: usage of output variances.\n")

  print("=" * 50)
  print("Performing training sample generation.\n")
  training_sample_size = 10
  point_evaluation_number = 15
  print("Input points number: %s, noisy function evaluations at each point number: %s." %
         (training_sample_size, point_evaluation_number))
  training_points, training_values = generate_training_sample(training_sample_size, point_evaluation_number)
  print("Training sample generated.\n")

  print("=" * 50)
  print("Performing estimation of noise variances and function values at input points.\n")
  training_sample = (training_points,) + estimate_noise_variances(training_values)
  print("Output variances and function values estimated.\n")

  print("=" * 50)
  print("Set some training sample output variances to NaNs")
  nan_points_number = 4
  training_sample = (training_sample[0],
                     training_sample[1],
                     mix_in_nans(training_sample[2], nan_points_number))

  print("=" * 50)
  print("Training GTApprox models...")
  models = build_models(*training_sample)
  print("GTApprox models trained.")

  print("=" * 50)
  print("Validating models...")
  test_sample_size = 1000
  print("Generating a test sample (%s points)..." % test_sample_size)
  test_points = np.linspace(0, 1, test_sample_size).reshape(-1, 1)
  test_values = target_function(test_points)
  test_sample = (test_points, test_values)
  print("Test sample generated.")

  print("=" * 50)
  print("Model validation...")
  validate_models(models, test_sample)
  print("Models validated.")

  print("=" * 50)
  print("Plotting...")
  plot(models, training_sample + test_sample)
  print("=" * 50)
  print("\nFinished pSeven Core for Python example: usage of output variances.\n")
#[11]

if __name__ == "__main__":
  main()
