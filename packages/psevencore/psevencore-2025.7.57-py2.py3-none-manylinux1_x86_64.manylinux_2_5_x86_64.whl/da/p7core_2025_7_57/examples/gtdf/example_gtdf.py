#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#


def usage_example():
  """
  Example of usage
  """

  def getTrainData(sample_size, dim, noisy):
    import random
    x, f  = [], []
    for _ in range(sample_size):
      x.append([random.uniform(0, 1) for _ in range(dim)])
      f.append(x[-1][0] + sum(v**2 for v in x[-1][1:]))
      if noisy:
        f[-1] += x[-1][-1]
    return x, f

  dim = 3
  sample_size_hf = 10
  sample_size_lf = sample_size_hf * 10
  # Prepare high fidelity sample
  x_hf, f_hf = getTrainData(sample_size_hf, dim, False)
  # Prepare low fidelity sample
  x_lf, f_lf = getTrainData(sample_size_lf, dim, True)

  from da.p7core import gtdf
  from da.p7core.loggers import StreamLogger
  # create builder
  builder = gtdf.Builder()
  # set logger, by default output of StreamLogger -- to sys.stdout
  builder.set_logger(StreamLogger())
  # train model
  model = builder.build(x_hf, f_hf, x_lf, f_lf, options={'GTDF/loglevel': 'Info'})

  # calculate errors
  def calc_rms_error(model, x_sample, f_sample):
    import math
    assert(model.size_f == 1)
    f_evaluated = [model.calc(x)[0] for x in x_sample]
    squared_errors = [(f_1 - f_2)**2 for f_1, f_2 in zip(f_sample, f_evaluated)]
    return math.sqrt(sum(squared_errors) / len(squared_errors))

  sample_size_test = 1000
  x_hf, f_hf = getTrainData(sample_size_test, dim, False)
  x_lf, f_lf = getTrainData(sample_size_test, dim, True)
  print('RMS errors: %s' % ('-'*30))
  print('HF rms error: %.15g' % calc_rms_error(model, x_hf, f_hf))
  print('LF rms error: %.15g' % calc_rms_error(model, x_lf, f_lf))

  # print info about model
  print(str(model))


def main():
  """
  Example of GTDF usage.
  """
  import random
  random.seed(100)
  print('GTDF usage example: %s\n' % ('=' * 40))
  usage_example()

if __name__ == "__main__":
  main()
