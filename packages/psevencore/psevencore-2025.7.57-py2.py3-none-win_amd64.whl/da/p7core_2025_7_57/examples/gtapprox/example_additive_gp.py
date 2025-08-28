#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
pSeven Core for Python example: exploiting specific function structure.

This example demonstrates how one can benefit from incorporating
specific function structure into GTApprox model construction.
We consider a problem of approximating the target function f(x_1, x_2):
  f(x_1, x_2) = sin(10 * x_1) + sin(10 * x_2).
As this function has additive structure we can benefit
from usage of Additive covariance function for GP technique.

For the target function we construct surrogate models using 3 covariance functions
available in pSeven Core GT Approx:
weighted $L_p$, Mahalanobis and Additive covariance functions.

For all cases we calculate the relative root-mean-squared (RRMS) error
and plot contour projections of obtained approximations.
Comparisons from both points of view show that usage of Additive covariance function
significantly improve approximation quality:
we see that RRMS values for additive covariance function is lower that that for other covariance functions and
approximation for additive covariance function is almost indistinguishable from the target function.
"""

#[0] required imports
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

from da.p7core import gtapprox
#[0]

#[1] definition of the target function
def target_function(x):
  """
  Example target function with additive structure.

  Args:
    x: 2D NumPy array.

  Returns:
    An array of the target function values.
    Number of elements in output array coincides with number of input points.
  """
  result = np.sum(np.sin(10 * x), axis=1)
  return result
#[1]

#[2]
def construct_models(training_points, training_values):
  """
  Construct required surrogate models with pSeven Core GT Approx.

  Args:
    training_points: training points, 2D NumPy array.
    training_values: training values, NumPy array.

  Returns:
    three constructed surrogate model
  """
  builder = gtapprox.Builder()
  print("Construct surrogate model with default options...")
  default_model = builder.build(training_points, training_values, {})

  print("Construct surrogate model with Mahalanobis covariance function...")
  mahalanobis_covariance_function_model = builder.build(training_points, training_values,
                                                        {"GTApprox/GPType" : "Mahalanobis"})

  print("Construct surrogate model with Additive covariance function...")
  additive_covariance_function_model = builder.build(training_points, training_values,
                                                     {"GTApprox/GPType" : "Additive"})
  return (default_model,
          mahalanobis_covariance_function_model,
          additive_covariance_function_model)
#[2]

#[3]
def validate_models(models):
  """
  Calculate RRMS errors of constructed surrogate models for a test sample
  and correlations between true values and outputs of the constructed surrogate models.

  Args:
    models: a tuple which contains surrogate models constructed with GT Approx .
  """
  (default_model,
   mahalanobis_covariance_function_model,
   additive_covariance_function_model) = models

  print("Test sample generation...")
  test_points = np.random.rand(1000, 2)
  test_values = target_function(test_points)
  test_sample = (test_points, test_values)

  print("Test sample validation result...")
  print("RRMS error for GTApprox model with default options: %s" %
        (default_model.validate(*test_sample)["RRMS"][0]))
  print("RRMS error for GTApprox model with Mahalanobis covariance function: %s" %
        (mahalanobis_covariance_function_model.validate(*test_sample)["RRMS"][0]))
  print("RRMS error for GTApprox model with Additive covariance function: %s" %
        (additive_covariance_function_model.validate(*test_sample)["RRMS"][0]))
#[3]

def plot(models, training_sample):
  """
  Show and save a set of contour plots dedicated to make clear difference between constructed models.

  Args:
    models: a tuple which contains constructed with GT Approx models.
    training_sample: training points and training values used during the surrogate models construction.
  """
  #[4]
  def plot_contour_figure(test_points, test_values, training_points, title):
    """
    Plot a single contourf subplot for specified values.

    Args:
      test_points: 2d array of test tensor points to plot.
      test_values: vector array of test tensor values to plot.
      training_points: design of experiments for the training sample.
    """
    ax = figure_handle.add_subplot(2, 2, index + 1)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    # Set text for subplot
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("$x_1$", fontsize=16)
    ax.set_ylabel("$x_2$", fontsize=16)

    # Contour plot for the given data
    ax.contourf(test_points[:, 0].reshape(mesh_size[0], mesh_size[1]),
                test_points[:, 1].reshape(mesh_size[0], mesh_size[1]),
                test_values.reshape(mesh_size[0], mesh_size[1]),
                levels=contour_levels)

    # Add training sample scatter
    ax.scatter(training_points[:, 0], training_points[:, 1],
               s=60, vmin=0, vmax=1, linewidth=1.5,
               c=(training_values - min_value) / (max_value - min_value))
  #[4]

  (default_model,
   mahalanobis_covariance_function_model,
   additive_covariance_function_model) = models
  training_points, training_values = training_sample

  print("Sample for plotting generation...")
  mesh_size = [60, 60]
  firstDimensionPoints, secondDimensionPoints = np.meshgrid(np.linspace(0, 1, mesh_size[0]),
                                                            np.linspace(0, 1, mesh_size[1]))
  test_points = np.concatenate((firstDimensionPoints.reshape(-1, 1), secondDimensionPoints.reshape(-1, 1)), axis=1)
  test_values = target_function(test_points)
  figure_handle = plt.figure(figsize=(12, 12))
  figure_handle.suptitle('Additive GP', fontsize = 18)

  # get model outputs
  print("Get constructed models' outputs...")
  test_values_deafult_model = default_model.calc(test_points)
  test_values_mahalanobis_cf_model = mahalanobis_covariance_function_model.calc(test_points)
  test_values_additive_cf_model = additive_covariance_function_model.calc(test_points)
  test_values_array = [test_values,
                       test_values_deafult_model,
                       test_values_mahalanobis_cf_model,
                       test_values_additive_cf_model]

  # prepare information for plotting
  title_names_array = ["Target function",
                       "Default (weighted Lp) covariance function approximation",
                       "Mahalanobis covariance function approximation",
                       "Additive covariance function approximation"]

  print("Set contour levels' colors for contour plot")
  min_value = min((np.min(x) for x in test_values_array))
  max_value = max((np.max(x) for x in test_values_array))
  contour_levels_number = 15
  contour_levels = np.linspace(min_value, max_value, contour_levels_number)

  print("Draw subplots by turn...")
  for index, current_values in enumerate(test_values_array):
    print("%s to be plotted..." % title_names_array[index])
    plot_contour_figure(test_points, current_values, training_points, title_names_array[index])

  print("Saving obtained plot...")
  format_string = "png"
  plt.savefig("additive_Gp_example." + format_string, format=format_string)
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()
  plt.close(figure_handle)

#[5-0]
def main():
  """
  Main function plot a set of contour plots for constructed surrogate models and the target function
  """
  np.random.seed(1)

  print("\npSeven Core for Python example: exploiting specific function structure.\n")

  #[5-1] generate training sample
  print("=" * 50)
  print("Training sample generation...")
  training_points = np.random.rand(15, 2)
  training_values = target_function(training_points)
  training_sample = (training_points, training_values)

  #[5-2] Construct surrogate models
  print("=" * 50)
  print("Surrogate models construction...")
  models = construct_models(*training_sample)

  #[5-3] Calculate RRMS errors for test sample and constructed models
  print("=" * 50)
  print("Model validation...")
  validate_models(models)
  print("Models validated.")

  #[5-4] Plot results
  print("=" * 50)
  print("Plot results...")
  plot(models, training_sample)
  print("=" * 50)
  print("\nFinished pSeven Core for Python example: exploiting specific function structure.\n")
#[5-5]

if __name__ == "__main__":
  main()

