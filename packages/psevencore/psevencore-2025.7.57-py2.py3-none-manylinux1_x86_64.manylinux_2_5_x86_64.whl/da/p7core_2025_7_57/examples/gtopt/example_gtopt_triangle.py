#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
6 variables geometrical test case:
fit a triangle of minimum size around two non intersecting circles of unit radius
(assume w.l.o.g. that circle centers are located at (-1,1) and (1,1))
"""

from da.p7core import gtopt
from da.p7core import loggers
from pprint import pprint
from math import exp, sqrt, cos, sin, fabs
import os
import matplotlib.pyplot as plt

class CirclesInTriangleExampleProblem(gtopt.ProblemConstrained):
  def prepare_problem(self):
    self.enable_history()
    #coordinates of triangle vertices
    self.add_variable((1.5, 6.5), 5.0, 'x0')
    self.add_variable((-0.75, 0.75), -0.1, 'y0')
    self.add_variable((-0.75, 0.75), -0.1, 'x1')
    self.add_variable((1.5, 6.5), 5.0, 'y1')
    self.add_variable((-6.5, -1.5), -5.0, 'x2')
    self.add_variable((-0.75, 0.75), -0.1, 'y2')
    #find a triangle with minimal area
    self.add_objective('area')
    # define 6 constraints (distances from circle centers to sides of the triangle (these should be >= 1)
    for i in range(6):
      self.add_constraint((1.0, None), 'd' + str(i + 1))
    # area of triangle must be bigger than the area of circles
    self.add_constraint((6.2831854, None), 'areacon')

  def define_objectives(self, v):
    v = dict(zip(self.variables_names(), v))
    # triangle area
    return 0.5 * (v['x0'] * (v['y1'] - v['y2']) + v['x1'] * (v['y2'] - v['y0']) + v['x2'] * (v['y0'] - v['y1']))

  def define_constraints(self, v):
    v = dict(zip(self.variables_names(), v))
    con = {}
    # triangle centred on (1,1) dist from lines (want > radius = 1)
    con['d1'] = fabs((v['x1'] - v['x0']) * (v['y0'] - 1.0) - (v['x0'] - 1.0) * (v['y1'] - v['y0'])) / sqrt((v['x1'] - v['x0'])**2 + (v['y1'] - v['y0'])**2)
    con['d2'] = fabs((v['x2'] - v['x1']) * (v['y1'] - 1.0) - (v['x1'] - 1.0) * (v['y2'] - v['y1'])) / sqrt((v['x2'] - v['x1'])**2 + (v['y2'] - v['y1'])**2)
    con['d3'] = fabs((v['x0'] - v['x2']) * (v['y2'] - 1.0) - (v['x2'] - 1.0) * (v['y0'] - v['y2'])) / sqrt((v['x0'] - v['x2'])**2 + (v['y0'] - v['y2'])**2)
    # triangle centred on (-1,1) dist from lines (want > radius = 1)
    con['d4'] = fabs((v['x1'] - v['x0']) * (v['y0'] - 1.0) - (v['x0'] + 1.0) * (v['y1'] - v['y0'])) / sqrt((v['x1'] - v['x0'])**2 + (v['y1'] - v['y0'])**2)
    con['d5'] = fabs((v['x2'] - v['x1']) * (v['y1'] - 1.0) - (v['x1'] + 1.0) * (v['y2'] - v['y1'])) / sqrt((v['x2'] - v['x1'])**2 + (v['y2'] - v['y1'])**2)
    con['d6'] = fabs((v['x0'] - v['x2']) * (v['y2'] - 1.0) - (v['x2'] + 1.0) * (v['y0'] - v['y2'])) / sqrt((v['x0'] - v['x2'])**2 + (v['y0'] - v['y2'])**2)
    # constraint on area > area of circles
    con['areacon'] = 0.5 * (v['x0'] * (v['y1'] - v['y2']) + v['x1'] * (v['y2'] - v['y0']) + v['x2'] * (v['y0'] - v['y1']))
    return [con[k] for k in self.constraints_names()]


def run_circle_problem():
  optimizer = gtopt.Solver()
  optimizer.set_logger(loggers.StreamLogger())
  #initialize problem
  problem = CirclesInTriangleExampleProblem()
  # solve problem and get result
  result = optimizer.solve(problem)
  # print general info about result
  print(str(result))
  #different ways to work with solution
  opt_con = result.optimal.c
  print('constraints: %s' % opt_con)
  print('constraints names: %s' % result.names.c)
  print('%s:  %f' % (problem.constraints_names()[0], opt_con[0][0]))
  hist = [t[0:6] for t in problem.history]
  return result, hist


def plot(result, hist):
  plt.clf()
  fig = plt.figure(1)
  ax = fig.add_subplot(111)
  ax.axis('equal')
  title = 'Circles in triangle'
  plt.title(title)
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  circle1 = plt.Circle((-1, 1), 1, facecolor='none',
              edgecolor='r', linewidth=1.5, alpha=0.5)
  ax.add_patch(circle1)
  circle2 = plt.Circle((1, 1), 1, facecolor='none',
              edgecolor='r', linewidth=1.5, alpha=0.5)
  ax.add_patch(circle2)
  for i in range(len(hist)):
    if i%10 == 0:
      points = hist[i]
      x = [points[0], points[2], points[4], points[0]]
      y = [points[1], points[3], points[5], points[1]]
    if i == 0:
      ax.plot(x,y, 'b--', linewidth=0.6, label = 'Opimization Steps')
    else :
      ax.plot(x,y, 'b--', linewidth=0.6)
  points = result.optimal.x[0]
  x = [points[0], points[2], points[4], points[0]]
  y = [points[1], points[3], points[5], points[1]]
  ax.plot(x,y, 'r-', linewidth=2, label = 'Optimal Solution')
  ax.legend(loc = 'best')
  plt.title(title)
  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()


def main():
  print('Find minimum function')
  print('=' * 60)
  result, hist = run_circle_problem()
  plot(result, hist)
  print('=' * 60)
  print('Finished!')

if __name__ == "__main__":
  main()
