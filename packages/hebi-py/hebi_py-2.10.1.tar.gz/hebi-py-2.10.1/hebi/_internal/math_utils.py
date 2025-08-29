# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------


import math
import numpy as np


def det_3x3(a: 'np.ndarray'):
  return (a[0][0] * (a[1][1] * a[2][2] - a[2][1] * a[1][2])
         -a[1][0] * (a[0][1] * a[2][2] - a[2][1] * a[0][2])
         +a[2][0] * (a[0][1] * a[1][2] - a[1][1] * a[0][2]))

def norm_square_mat(a: 'np.ndarray'):
  acc = 0
  for el in a:
    acc += el*el
  return math.sqrt(acc)


def is_finite(m: 'np.ndarray'):
  """Determine if the input has all finite values.

  :param m: a matrix or array of any shape and size
  :type m:  list, numpy.ndarray, ctypes.Array
  """

  res = np.isfinite(m)
  if isinstance(res, bool):
    return res
  return res.all()


def is_so3_matrix(m: 'np.ndarray'):
  """Determine if the matrix belongs to the SO(3) group. This is found by
  calculating the determinant and seeing if it equals 1.

  :param m: a 3x3 matrix
  :type m:  list, numpy.ndarray, ctypes.Array
  """
  try:
    det = det_3x3(m)

    # Arbitrarily determined. This may change in the future.
    tolerance = 1e-5
    diff = abs(det-1.0)

    #dist_from_identity = np.linalg.norm(np.eye(3) - m @ m.T)
    diff_mat = m @ m.T
    diff_mat[0, 0] -= 1.0
    diff_mat[1, 1] -= 1.0
    diff_mat[2, 2] -= 1.0
    dist_from_identity = norm_square_mat(diff_mat)

    return diff < tolerance and dist_from_identity < tolerance
  except Exception as e:
    return False
