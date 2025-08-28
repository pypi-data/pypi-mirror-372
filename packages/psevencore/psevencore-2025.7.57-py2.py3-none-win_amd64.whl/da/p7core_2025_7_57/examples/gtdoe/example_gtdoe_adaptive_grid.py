#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Example: how to use adaptive design of experiments on a grid.
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from da.p7core import gtapprox, gtdoe
from da.p7core.blackbox import Blackbox
from da.p7core.loggers import StreamLogger, LogLevel

class UserBlackbox(Blackbox):
  def prepare_blackbox(self):
    """Required blackbox method. Defines design variables and responses."""
    self.add_variable(bounds=(0, 1))
    self.add_variable(bounds=(0, 1))
    self.add_response()

  def evaluate(self, design_points):
    """Required blackbox method. Returns an array of function values."""
    result = []
    for design_point in design_points:
      x, y = design_point
      result.append((x + 1)**2 + (y - 1)**2)
    return result

def main():
  budget = 30
  generator = gtdoe.Generator()
  generator.set_logger(StreamLogger())
  bbox = UserBlackbox()
  # We define levels as evenly distributed values in some interval
  #
  # Note that some levels are outside of generation bounds. They will be ignored during the generation.
  levels_x = np.linspace(0, 1, 20).tolist()
  levels_y = np.linspace(0, 1.1, 10).tolist()
  # To generate adaptive design on a grid instead of continous space, we need to set only one option
  generator.options.set({
    "GTDoE/CategoricalVariables": [0, levels_x, 1, levels_y]
  })
  # As blackbox is provided, adaptive mode will be selected automatically
  result = generator.generate(bounds=bbox.variables_bounds(), budget=budget, blackbox=bbox)

  # Plot the results
  xx, yy = np.meshgrid(levels_x, levels_y)
  plt.plot(xx.ravel(), yy.ravel(), 'ko', label="Grid levels")
  plt.plot(result.points[:, 0], result.points[:, 1], 'rs', label="Selected points")
  plt.title("Adaptive DoE on grid")
  plt.xlabel("$x$", fontsize ="16")
  plt.ylabel("$y$", fontsize ="16")
  plt.legend()
  plt.xlim(-.1, 1.2)
  plt.ylim(-.1, 1.2)

  # Show plots if we may.
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    print("Close plot windows to finish.")
    plt.show()


if __name__ == "__main__":
  main()
