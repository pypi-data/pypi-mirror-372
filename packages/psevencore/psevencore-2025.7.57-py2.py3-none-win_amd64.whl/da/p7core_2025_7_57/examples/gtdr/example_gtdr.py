#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#


from da.p7core import gtdr
from da.p7core.loggers import StreamLogger, LogLevel
from da.p7core.blackbox import Blackbox
import random

def rms(x_one, x_two):
  """
  calculate root mean square error
  """
  import math
  tmp = [pow(x_one[i] - x_two[i], 2.) for i in range(len(x_one))]
  return math.sqrt(sum(tmp) / len(tmp))

class ExampleBlackbox(Blackbox):
  """
  Problem representation for GTDR builder in blackbox mode
  """
  def prepare_blackbox(self):
    # add new variable in problem
    self.add_variable((0, 1))
    self.add_variable((0, 1))
    self.add_variable((0, 1))
    # add new response in problem
    self.add_response()

  def evaluate(self, queryx):
    result = []
    for x in queryx:
      result.append(sum(x)**2)
    return result

def reduction_by_dim():
  """
  Example reduction dimension procedure with reduced dimension value specified by the User
  """
  # create data
  orig_dim = 5
  sample_size = 20
  data = [[random.random() for j in range(orig_dim)] for i in range(sample_size)]

  # create builder
  builder = gtdr.Builder()
  # set logger, by default output -- to sys.stdout
  builder.set_logger(StreamLogger())
  # create model
  model = builder.build(x=data, dim=2, options={'GTDR/MinImprove': '0.1', 'GTDR/LogLevel': 'Info'})
  #print info about model
  print(str(model))

  # print original and compressed size
  print("Original dim: %s" % model.original_dim)
  print("Compressed dim: %s" % model.compressed_dim)
  # usage of model
  original = [random.random() for j in range(orig_dim)]
  print("original: %s" % original)
  compressed = model.compress(original)
  print("compressed: %s" % compressed)
  decompressed = model.decompress(compressed)
  print("decompressed: %s" % decompressed)
  error = rms(original, decompressed)
  print("error: %s" % error)

  # save model to file
  model.save("GtdrModelByDim.dr")
  # load model from file
  loaded_model = gtdr.Model('GtdrModelByDim.dr')

def reduction_by_err():
  """
  Example reduction dimension procedure with automatic selection of reduced dimension value based on reconstruction error specified by the User
  """
  orig_dim = 5
  sample_size = 20
  data = [[random.random() for j in range(orig_dim)] for i in range(sample_size)]

  builder = gtdr.Builder()
  # alternate method how to set options
  builder.options.set( {'GTDR/MinImprove': '0.1', 'GTDR/LogLevel': 'Debug'} )
  desired_error = 0.2
  model = builder.build(x=data, error=desired_error)

  original = [random.random() for j in range(orig_dim)]
  print("original: %s" % original)
  compressed = model.compress(original)
  print("compressed: %s" % compressed)
  decompressed = model.decompress(compressed)
  print("decompressed: %s" % decompressed)
  error = rms(original, decompressed)
  print("error: %s" % error)
  err = rms([rms(x, model.decompress(model.compress(x))) for x in data], [0 for x in data])
  print('rms err = %s' % err)

  # save model to file
  model.save("GtdrModelByErr.dr")
  # load model from file
  loaded_model = gtdr.Model('GtdrModelByErr.dr')

def feature_extraction():
  """
  Construction of such dimension reduction procedure,
  which aims at keeping outputs for initial inputs and outputs for reconstructed inputs as close as possible
  """
  # prepare data
  orig_dim = 3

  sample_size = 50
  X = [[random.random() for j in range(orig_dim)] for i in range(sample_size)]
  def f(x):
    assert(len(x) == 3)
    linear_combination = sum(x)
    return [5 * linear_combination, linear_combination * linear_combination]
  F = [f(x) for x in X]

  builder = gtdr.Builder()
  model = builder.build(x=X, y=F, options={'GTDR/LogLevel': 'Debug'})

  original_x = [random.random() for j in range(orig_dim)]
  original_f = f(original_x)

  # use model
  compr_dim = 1
  compressed_x = model.compress(original_x, compr_dim)
  decompressed_x = model.decompress(compressed_x)
  decompressed_f = f(decompressed_x)
  print('compressed dimensionality: %d' % compr_dim)
  print("error by x: %g" % rms(original_x, decompressed_x))
  print("error by f: %g" % rms(original_f, decompressed_f))

  compr_dim = 2
  # new feature: default dimensionality for FE
  model = builder.build(x=X, y=F, dim=compr_dim, options={'GTDR/LogLevel': 'Debug'})
  assert(model.compressed_dim == compr_dim)

  # use model
  compressed_x = model.compress(original_x)
  decompressed_x = model.decompress(compressed_x)
  decompressed_f = f(decompressed_x)
  print('compressed dimensionality: %d' % compr_dim)
  print("error by x: %g" % rms(original_x, decompressed_x))
  print("error by f: %g" % rms(original_f, decompressed_f))

  # save model to file
  model.save("GtdrModelFE.dr")
  # load model from file
  loaded_model = gtdr.Model('GtdrModelFE.dr')

def feature_extraction_bb():
  """
  Based on blackbox input, constructs such dimension reduction procedure,
  that aims at keeping outputs for initial inputs and outputs for reconstructed inputs as close as possible
  """
  # prepare data
  bb = ExampleBlackbox()
  orig_dim = bb.size_x()
  compr_dim = 1

  original_x = [random.random() for j in range(orig_dim)]
  original_f = [bb.evaluate([original_x])[0]]

  builder = gtdr.Builder()
  # new feature: default dimensionality for FE
  model = builder.build(blackbox=bb, budget=1000, dim=compr_dim, options={'GTDR/LogLevel': 'Debug'})
  assert(model.compressed_dim == compr_dim)

  # use model
  compressed_x = model.compress(original_x)
  decompressed_x = model.decompress(compressed_x)
  decompressed_f = [bb.evaluate([decompressed_x])[0]]
  print('compressed dimensionality: %d' % compr_dim)
  print("error by x: %g" % rms(original_x, decompressed_x))
  print("error by f: %g" % rms(original_f, decompressed_f))

  # save model to file
  model.save("GtdrModelFEBB.dr")
  # load model from file
  loaded_model = gtdr.Model('GtdrModelFEBB.dr')

def main():
  """
  Example of GTDR usage.
  """
  random.seed(100)

  print("\n\n")
  print("="*60)
  print("\nReduction by dimension\n")
  reduction_by_dim()

  print("\n\n")
  print("="*60)
  print("\nReduction by error\n")
  reduction_by_err()

  print("\n\n")
  print("="*60)
  print("\nFeature extraction - blackbox mode\n")
  feature_extraction_bb()

  print("\n\n")
  print("="*60)
  print("\nFeature extraction\n")
  feature_extraction()

if __name__ == "__main__":
  main()
