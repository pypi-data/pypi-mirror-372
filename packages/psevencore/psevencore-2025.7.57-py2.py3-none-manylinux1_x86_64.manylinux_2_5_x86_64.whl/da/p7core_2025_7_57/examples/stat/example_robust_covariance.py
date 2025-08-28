#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

# Example of calculate_statistics usage.

#[0] required imports
from da.p7core import stat

import numpy as np
import matplotlib.pyplot as plt
import os
#[0]

#[1] plotting data
def plot_data(points11, points12, points21, points22, title):
  points11 = np.array(points11)
  points12 = np.array(points12)
  points21 = np.array(points21)
  points22 = np.array(points22)

  fig = plt.figure(figsize = (22, 10))

  subplt1 = fig.add_subplot(121)
  subplt1.scatter(points11[:, 0], points11[:, 1], s=100, marker='o', c='r')
  subplt1.scatter(points12[:, 0], points12[:, 1], s=100, marker='o', c='b')
  plt.legend(('Inliers', 'Outliers'))
  plt.title('Inliers and outliers for robust covariance')

  subplt2 = fig.add_subplot(122)
  subplt2.scatter(points21[:, 0], points21[:, 1], s=100, marker='o', c='r')
  subplt2.scatter(points22[:, 0], points22[:, 1], s=100, marker='o', c='b')
  plt.legend(('Inliers', 'Outliers'))
  plt.title('Inliers and outliers for empirical covariance')

  # save and show plots
  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()
#[1]

#[2-0] main worlflow
def main():
  #[2-1] sample generation
  print('Sample generation...')
  n_features = 2
  n_inliers = 100
  n_outliers = 20

  rand_gen = np.random.RandomState(0)
  inliers_mean = np.array([0, 0])
  inliers_std = [1, 2]
  inliers = rand_gen.randn(n_inliers, n_features)
  inliers = inliers * inliers_std + inliers_mean

  outliers_mean = np.array([4, 4])
  outliers_std = [2, 1]
  outliers = rand_gen.randn(n_outliers, n_features)
  outliers = outliers * outliers_std + outliers_mean

  sample = np.vstack((inliers, outliers))
  #[2-2] computing statistics
  print("Computing statistiscs...")
  stat_object = stat.Analyzer()
  statistics = stat_object.calculate_statistics(sample)
  statistics_robust = stat_object.calculate_statistics(sample, covariance='robust')

  print('Standard deviation of inliers (no correlation) is %s' % inliers_std)
  print('Computed standard deviation in case of empirical covariance is %s' % statistics.std)
  print('Computed standard deviation in case of robust covariance is %s' % statistics_robust.std)
  print('Computed matrix of correlation coefficients in case of empirical covariance is %s' % statistics.correlation)
  print('Computed matrix of correlation coefficients in case of robust covariance is %s' % statistics_robust.correlation)

  #[2-3] detecting outliers
  print('Detecting outliers...')
  robust_outlier_detection_result = stat_object.detect_outliers(sample, covariance='robust', confidence=0.9)
  robust_outliers_mask = robust_outlier_detection_result.outliers
  robust_inliers_mask = [not outlier for outlier in robust_outliers_mask]
  robust_detected_inliers = sample[np.where(robust_inliers_mask)]
  robust_detected_outliers = sample[np.where(robust_outliers_mask)]

  outlier_detection_result = stat_object.detect_outliers(sample, confidence=0.9)
  outliers_mask = outlier_detection_result.outliers
  inliers_mask = [not outlier for outlier in outliers_mask]
  detected_inliers = sample[np.where(inliers_mask)]
  detected_outliers = sample[np.where(outliers_mask)]

  #[2-4] plotting data
  plot_data(robust_detected_inliers, robust_detected_outliers, detected_inliers, detected_outliers, title='inliers_outliers')
  #[2-5]

if __name__ == "__main__":
  main()
