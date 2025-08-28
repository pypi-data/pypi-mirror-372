#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Example illustrates benefits of the GTApprox/MaxAxisRotations option usage.
"""

#[0] Required imports
import os
import sys
import numpy as np
from datetime import datetime

from da.p7core import gtapprox
from da.p7core.loggers import StreamLogger
#[0] imports end

#[1] Function to be approximated: normalized Rana's function with diagonal wrap
def rana(x):
  # Evaluate n-dimensional normalized Rana function.
  # Note 2D case can be reduced to the following formula:
  #          x1 * sin(sqrt(abs(x2 - x1 + 1))) * cos(sqrt(abs(x2 + x1 + 1)))
  #  + (x1 + 1) * cos(sqrt(abs(x1 - x2 + 1))) * sin(sqrt(abs(x2 + x1 + 1)))
  #  +       x2 * sin(sqrt(abs(x1 - x2 + 1))) * cos(sqrt(abs(x2 + x1 + 1)))
  #  + (x2 + 1) * cos(sqrt(abs(x2 - x1 + 1))) * sin(sqrt(abs(x2 + x1 + 1)))

  x  = np.array(x, dtype=float)
  xj = x[:, range(-1, x.shape[1] - 1)]
  t1 = np.sqrt(np.abs(xj - x + 1))
  t2 = np.sqrt(np.abs(xj + x + 1))
  return (x * np.sin(t1) * np.cos(t2) + (xj + 1.) * np.cos(t1) * np.sin(t2)).sum(axis=1).reshape((-1,1)) / x.shape[1]
#[1]

#[2] main workflow
def main():
  #[2-1] Generate training and validation data
  print("Generating train and validation datasets...")
  x_min, x_max = -450., -520. # both input coordinates have the same range
  train_x = square_grid(x_min, x_max, 8) # generate train input as full factorial 8-by-8 grid within [x_min, x_max] range
  train_y = rana(train_x) # evaluate true function at train input points
  validation_x = square_grid(x_min, x_max, 100) # generate validation input as full factorial 100-by-100 grid within [x_min, x_max] range
  validation_y = rana(validation_x) # evaluate true function at validation input points
  print("Done. Train data contain %d vectors while validation data contain %d vectors." % (train_x.shape[0], validation_x.shape[0]))
  #[2-1]

  #[2-2] Initialize  model builder
  print('Creating GTApprox Builder...')
  gtapprox_builder = gtapprox.Builder() # create the model builder object
  gtapprox_builder.set_logger(StreamLogger()) # attach console logger to the model builder

  # Manually select HDA technique. It is neither necessary nor optimal for this particular
  # simplified case, but usually it is the optimal choice for a huge multidimensional dataset.
  gtapprox_builder.options.set("GTApprox/Technique", "HDA")
  #[2-2]

  #[2-3] Create HDA approximation using default options.
  print("\n\nTraining HDA model with default options (note 'GTApprox/MaxAxisRotations'=0 by default)...")
  print("-" * 74)
  time_start = datetime.now()
  model_default = gtapprox_builder.build(train_x, train_y) # create model using default options (implies no axis rotations)
  time_default = datetime.now() - time_start
  print("-" * 74)
  #[2-3]

  #[2-4] Create HDA approximation using axis rotations.
  print("\n\nTraining HDA model with auto selection of the axis rotations number ('GTApprox/MaxAxisRotations'=-1)...")
  print("-" * 74)
  time_start = datetime.now()
  model_rotations = gtapprox_builder.build(train_x, train_y, options={"GTApprox/MaxAxisRotations": -1}) # create model with 'auto' selected number of axis rotations
  time_rotations = datetime.now() - time_start
  print("-" * 74)
  #[2-4]

  #[2-5] Comparing models built with and without axis rotations
  print("\n\nCalculating validation errors...")
  # The validate() method returns dictionary that maps the error metric name to the vector of outputwise errors values.
  errors_default = model_default.validate(validation_x, validation_y)
  errors_rotations = model_rotations.validate(validation_x, validation_y)
  print("-" * 74)
  print("| %-25s| %-20s | %-20s |" % ("", "Default options", "Use axis rotations"))
  print("-" * 74)
  # Print training time.
  print("| %-25s| %-20s | %-20s |" % ("Training time", time_default, time_rotations))
  # Print approximation technique selected by SmartSelection.
  print("| %-25s| %-20s | %-20s |" % ("Technique selected", model_default.details["Technique"], model_rotations.details["Technique"]))
  print("-" * 74)
  for error_name in sorted(errors_default.keys()):
    # Print error metric and its value. Note output of the model is 1-dimensional.
    print("| %-25s| %-20.5g | %-20.5g |" % (error_name, errors_default[error_name][0], errors_rotations[error_name][0]))
  print("-" * 74)
  #[2-5]

  #[2-7] Display 3D plots of models. The first argument of the helper function is dictionary: model title -> callable object evaluating function value.
  # So we can seamlessly mix models calc() method and pure Python rana() function.
  plot_3D({"Model built with default options": model_default.calc,
           "Model built with axis rotations": model_rotations.calc,
           "True normalized Rana's function with diagonal wrap": rana}, \
          train_x, train_y)
  #[2-7]

  #[2-8] Display contour plots.
  plot_2D({"Model built with default options": model_default.calc,
           "Model built with axis rotations": model_rotations.calc,
           "True normalized Rana's function with diagonal wrap": rana}, \
          train_x, train_y, [-400., -200., 0., 200., 400.])
  #[2-8]
#[2]

#[3] Helper function for 2D grid generation
def square_grid(x_min, x_max, n_x):
  x_factor = np.linspace(x_min, x_max, n_x).reshape(-1, 1)
  return np.hstack((np.repeat(x_factor, x_factor.shape[0], axis=0),
                    np.tile(x_factor, (x_factor.shape[0], 1))))
#[3]

#[4] Helper function for 3D plotting
def plot_3D(named_models, train_x, train_y):
  print('Plotting 3D charts...')
  try:
    # Try to import required matplotlib library
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    from matplotlib import cm

    fontsize = 10 # titles and labels font size
    train_dataset_color = (0., .5, 0., 1.0) # color of the trainign dataset points
    model_prediction_color = (0., 0., 1., 0.8) # color of the model values mesh
    background_color = (1., 1., 1., 1.) # plot background color

    # Create mesh grid for plotting model predictions
    x_mesh = np.meshgrid(np.linspace(train_x[:, 1].min(), train_x[:, 1].max(), 100),
                         np.linspace(train_x[:, 1].min(), train_x[:, 1].max(), 100))

    # Convert mesh grid to the gtapprox.Model.calc()-compatible representation
    model_x = np.hstack((x_mesh[0].flatten().reshape(-1, 1), x_mesh[1].flatten().reshape(-1, 1)))

    figures_list = [] # special list of objects that should be stored until plot is removed

    # Enumerate model names. The model index is only needed for PNG file name generation.
    for model_index, model_name in enumerate(named_models):
      # Create new plot window.
      figure = plt.figure(figsize=(10., 7.), facecolor=background_color, edgecolor=background_color)

      # Configure 3D plot.
      subplot = figure.add_subplot(111, projection='3d')
      subplot.tick_params(labelsize=fontsize)
      subplot.set_xlabel("x1", fontsize=fontsize)
      subplot.set_ylabel("x2", fontsize=fontsize)
      subplot.set_zlabel("f(x1, x2)", fontsize=fontsize)

      # draw scatter plot of the training dataset
      plot_dataset = subplot.scatter(train_x[:, 0], train_x[:, 1], train_y[:, 0], color=train_dataset_color, s=4)

      # Calculate model predictions. Note it returns N-by-1 dimensional matrix while wireframe mesh requires
      # mesh with the same shape as x_mesh[0] and x_mesh[1]. Fortunately order of points in flatten matrix
      # is the same for x_mesh and model predictions, so we can reshape to the x_mesh[0].shape.
      model_predictions = named_models[model_name](model_x).reshape(x_mesh[0].shape)

      # draw wireframe mesh of models predictions
      plot_predictions = subplot.plot_wireframe(x_mesh[0], x_mesh[1], model_predictions, color=model_prediction_color, linewidth=0.2)

      # Setup legend and title.
      figure.legend(handles=[plot_dataset, plot_predictions], \
                    labels=['Train dataset', 'Model predictions'], prop={'size': fontsize})
      figure.suptitle(model_name, fontsize=(fontsize+2))

      # Make some layout cosmetics.
      figure.tight_layout()
      figure.get_axes()[0].view_init(azim=-135., elev=60.)

      # Generate file name.
      filename = 'gtapprox_example_axis_rotations_contour_%d.png' % model_index

      # Python 2/3 compatibility workarond
      try:
        filename = os.path.join(os.getcwdu(), filename)
      except AttributeError:
        filename = os.path.join(os.getcwd(), filename)

      # Save figure as PNG file.
      figure.savefig(filename)
      print('Plot of the "%s" is saved to %s' % (model_name, filename))

      # Store figure object until plot is shown.
      figures_list.append(figure)

    if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
      plt.show()
  except ImportError:
    print("Plotting is disabled due to absence of the matplotlib library.")
  except:
    print("Failed to plot figure: %s" % sys.exc_info[1])
#[4]

#[5] Helper function for contour plotting
def plot_2D(named_models, train_x, train_y, levels):
  print('Plotting contour charts...')
  try:
    # Try to import required matplotlib library
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    from matplotlib import cm

    fontsize = 10 # titles and labels font size
    train_dataset_color = (0., .5, 0., 1.0) # color of the trainign dataset points
    background_color = (1., 1., 1., 1.) # plot background color

    # Create mesh grid for plotting model predictions. We need a lot of points to generate accurate contour plot.
    x_mesh = np.meshgrid(np.linspace(train_x[:, 1].min(), train_x[:, 1].max(), 400),
                         np.linspace(train_x[:, 1].min(), train_x[:, 1].max(), 400))

    # Convert mesh grid to the gtapprox.Model.calc()-compatible representation
    model_x = np.hstack((x_mesh[0].flatten().reshape(-1, 1), x_mesh[1].flatten().reshape(-1, 1)))

    figures_list = [] # special list of objects that should be stored until plot is removed

    # Enumerate model names. The model index is only needed for PNG file name generation.
    for model_index, model_name in enumerate(named_models):
      # Create new plot window.
      figure = plt.figure(figsize=(10., 7.), facecolor=background_color, edgecolor=background_color)

      # Configure 2D plot.
      subplot = figure.add_subplot(111)
      subplot.tick_params(labelsize=fontsize)
      subplot.set_xlabel("x1", fontsize=fontsize)
      subplot.set_ylabel("x2", fontsize=fontsize)

      # Draw scatter plot of the training dataset.
      plot_dataset = subplot.scatter(train_x[:, 0], train_x[:, 1], color=train_dataset_color, s=4)

      # Calculate model predictions. Note it returns N-by-1 dimensional matrix while contour plot requires
      # mesh with the same shape as x_mesh[0] and x_mesh[1]. Fortunately order of points in flatten matrix
      # is the same for x_mesh and model predictions, so we can reshape to the x_mesh[0].shape.
      model_predictions = named_models[model_name](model_x).reshape(x_mesh[0].shape)

      # Draw models predictions as contour plot.
      levels = sorted(levels)
      plot_predictions = subplot.contour(x_mesh[0], x_mesh[1], model_predictions, cmap=cm.coolwarm, levels=levels)
      plot_predictions.clabel(inline=1, fontsize=(fontsize-2))

      # Setup legend and title.
      legend_labels = ['Train dataset']
      legend_colors = [plot_dataset]

      for level in zip(levels):
        legend_labels.append('f(x1, x2) = %g' % level)

      figure.legend(handles=legend_colors, labels=legend_labels, prop={'size': fontsize})
      figure.suptitle(model_name, fontsize=(fontsize+2))

      # Generate file name.
      filename = 'gtapprox_example_axis_rotations_contour_%d.png' % model_index

      # Python 2/3 compatibility workarond
      try:
        filename = os.path.join(os.getcwdu(), filename)
      except AttributeError:
        filename = os.path.join(os.getcwd(), filename)

      # Save figure as PNG file.
      figure.savefig(filename)
      print('Plot of the "%s" is saved to %s' % (model_name, filename))

      # Store figure object until plot is shown.
      figures_list.append(figure)

    if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
      plt.show()
  except ImportError:
    print("Plotting is disabled due to absence of the matplotlib library.")
  except:
    print("Failed to plot figure: %s" % sys.exc_info[1])
#[5]

if __name__ == "__main__":
  main()
