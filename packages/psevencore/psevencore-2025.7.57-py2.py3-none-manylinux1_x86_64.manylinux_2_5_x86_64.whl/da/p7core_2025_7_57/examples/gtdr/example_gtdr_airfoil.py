#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

# pSeven Core GTDR: basic example of airfoil compression
"""
Example of basic GTDR usage for airfoil compression/decompression
and new airfoil generation.
"""

#[0]
from da.p7core import gtdr
from da.p7core import loggers

import numpy as np
import matplotlib.pyplot as plt

import os
#[0]

#[1]
def build_models(data, reduced_dimensions):
  """
  Build GTDR models for various reduced (target) dimensions using
  dimension-based DR. All GTDR options are left default.
  """
  # Create GTDR model builder:
  builder = gtdr.Builder()
  # Create logger and connect it to builder:
  logger = loggers.StreamLogger()
  builder.set_logger(logger)
  # Build models:
  models = []
  for dim in reduced_dimensions:
    print('=' * 79)
    print('Building GTDR model for target dimension %d...' % (dim))
    print('=' * 79)
    model = builder.build(x = data, dim = dim)
    print('=' * 79)
    # Check the reduced dimension for the model just built:
    print('Reduced dimension: %d' % (model.compressed_dim))
    # Check the reconstruction error value:
    rec_error = model.info['DimensionReduction'] \
                          ['Training Set Accuracy'] \
                          ['Compression/decompression error (L2-norm)']
    print('Average reconstruction error: %s' % (rec_error))
    print('=' * 79)
    models.append(model)

  return models
#[1]

#[2]
def reconstruct_airfoils(models, ref_airfoil):
  """
  Apply compression/decompression to the reference airfoil
  using GTDR models with different reduced dimensions.

  Returns a list of tuples (dimension, airfoil).
  """
  reconstructed_airfoils = []
  for m in models:
    # Get reduced dimension from model info:
    dim = m.compressed_dim
    # Reconstruct (compress and decompress) an airfoil:
    reconstructed = m.decompress(m.compress(ref_airfoil))
    reconstructed_airfoils.append((dim, reconstructed))

  return reconstructed_airfoils
#[2]

#[3]
def generate_airfoils(num, model, ref_data):
  """
  Generate airfoils by taking a random vector in the compressed design space
  and decompressing it to the original dimension using the given GTDR model.

  This implementation is very crude: compressed vector generation algorithm
  drastically affects the quality of results, and straightforward
  randomization, like the one in this method, in fact produces low-quality
  results.

  Despite this, the probability of generating a correct airfoil with this
  method is high enough.
  """
  # Compress the reference data sample to determine the box bounds
  # in the compressed design space:
  comp_data = model.compress(ref_data)
  comp_dim = model.compressed_dim
  # All vectors from the reference sample, when compressed, are bound
  # to this box:
  x_min = np.min(comp_data, axis=0)
  x_max = np.max(comp_data, axis=0)
  # We will shrink the compressed design space a bit to exclude worst points
  # (points which are too close to the box bounds):
  shrink_by = 0.15
  x_min *= 1 - shrink_by
  x_max *= 1 - shrink_by

  # Generate:
  generated_airfoils = []
  for _ in range(num):
    # Random vector in the compressed space bound to (x_min, x_max):
    rnd_afl = np.multiply(np.random.rand(comp_dim), x_max - x_min) + x_min
    # Decompress it to get an airfoil in original design space:
    rnd_afl = model.decompress(rnd_afl)
    generated_airfoils.append(rnd_afl)

  return generated_airfoils
#[3]

#[4]
def plot_results(mesh, ref_airfoil, rec_airfoils, gen_airfoils):
  """
  Plot the reference airfoils, reconstructed airfoils and new generated
  airfoil vs the x-mesh.
  """
  fig = plt.figure(1)
  fig.subplots_adjust(left=0.2, wspace=0.6, hspace=0.6)
  # First subplot, reference and reconstructed airfoils:
  plt.subplot(211)
  plt.plot(mesh, ref_airfoil, label = 'Reference')
  for dim, afl in rec_airfoils:
    plt.plot(mesh, afl, label = 'Dimension: %s' % (dim))
  plt.legend(loc = 'best', prop={'size':8})
  plt.title('Reconstructed Airfoils')
  # Second subplot, generated airfoils:
  plt.subplot(212)
  for afl in gen_airfoils:
    plt.plot(mesh, afl)
  plt.title('Generated Airfoils')
  # Save the plot to current working directory:
  plot_name = 'gtdr_airfoils_example'
  plt.savefig(plot_name)
  print('Plot saved to %s.png' % os.path.join(os.getcwd(), plot_name))
  # Show the plot:
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    print('Close the plot window to finish.')
    plt.show()
#[4]

#[m]
def main():
  # Various reduced (target) dimensions for testing the reconstruction
  # accuracy of GTDR models:
  dimensions = [1, 3, 5, 7]

  # Locate resources:
  script_path = os.path.dirname(os.path.realpath(__file__))
  train_afl_path = os.path.join(script_path, 'airfoils.csv')
  ref_afl_path = os.path.join(script_path, 'afl_test.csv')

  # Load training data:
  print('=' * 79)
  print('Loading airfoil data for training...')
  print('=' * 79)
  train_airfoils = np.loadtxt(train_afl_path, delimiter=',')
  print('Original dimension: %d' % len(train_airfoils[0]))

  # Load the x-mesh (first row) and a reference airfoil (second row)
  # from a CSV file.
  print('=' * 79)
  print('Loading x-mesh and reference airfoil...')
  print('=' * 79)
  mesh, ref_airfoil = np.loadtxt(ref_afl_path, delimiter=',')

  # Build models of specified dimensions:
  print('=' * 79)
  print('Building GTDR models for target dimensions: %s' % (dimensions))
  print('=' * 79)
  models = build_models(train_airfoils, dimensions)

  # Reconstruction:
  print('=' * 79)
  print('Reconstructing the reference airfoil (dimensions: %s).' % (dimensions))
  print('=' * 79)
  reconstructed_airfoils = reconstruct_airfoils(models, ref_airfoil)

  # Generation - select the model (determines generation space dimensionality)
  # and the number of airfoils to generate:
  gen_model = models[3]
  num = 3
  dim = gen_model.compressed_dim
  print('=' * 79)
  print('Generating %s new airfoils in %s-dimensional space...' % (num, dim))
  print('=' * 79)
  gen_airfoils = generate_airfoils(num, gen_model, train_airfoils)

  # Finally, make the plots:
  plot_results(mesh, ref_airfoil, reconstructed_airfoils, gen_airfoils)

if __name__ == '__main__':
  main()
#[m]
