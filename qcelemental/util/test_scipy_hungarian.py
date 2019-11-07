# [Apr 2019] stolen directly from scipy so I can test getting an array back
#   https://github.com/scipy/scipy/blob/master/scipy/optimize/tests/test_hungarian.py
#   * change imports to local
#   * skip importing and testing `matrix`
#   * add testing of reduced cost for non-T (reduced matrix for T is different)

# Author: Brian M. Clapper, G. Varoquaux, Lars Buitinck
# License: BSD

import numpy as np
from numpy.testing import assert_array_equal
from pytest import raises as assert_raises

from qcelemental.util.scipy_hungarian import linear_sum_assignment


def test_linear_sum_assignment():

    # fmt: off
    data = [
        # Square
        ([[400, 150, 400],
          [400, 450, 600],
          [300, 225, 300]],
         [150, 400, 300],
         [[250,   0, 175],
          [  0,  50, 125],
          [ 75,   0,   0]]
         ),

        # Rectangular variant
        ([[400, 150, 400, 1],
          [400, 450, 600, 2],
          [300, 225, 300, 3]],
         [150, 2, 300],
         [[102,   0, 102,   0],
          [101, 299, 301,   0],
          [  0,  73,   0,   0]]
         ),

        # Square
        ([[10, 10, 8],
          [9, 8, 1],
          [9, 7, 4]],
         [10, 1, 7],
         [[0, 0, 1],
          [5, 4, 0],
          [2, 0, 0]]
         ),

        # Rectangular variant
        ([[10, 10, 8, 11],
          [9, 8, 1, 1],
          [9, 7, 4, 10]],
         [10, 1, 4],
         [[0, 0, 0, 3],
          [6, 5, 0, 0],
          [3, 1, 0, 6]]
         ),

        # n == 2, m == 0 matrix
        ([[], []],
         [],
         [[], []]),
    ]
    # fmt: on

    for cost_matrix, expected_cost, expected_reduced_cost_matrix in data:

        cost_matrix = np.array(cost_matrix)
        (row_ind, col_ind), reduced_cost_matrix = linear_sum_assignment(cost_matrix, return_cost=True)
        assert_array_equal(row_ind, np.sort(row_ind))
        assert_array_equal(expected_cost, cost_matrix[row_ind, col_ind])
        assert_array_equal(expected_reduced_cost_matrix, reduced_cost_matrix)

        cost_matrix = cost_matrix.T
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        assert_array_equal(row_ind, np.sort(row_ind))
        assert_array_equal(np.sort(expected_cost), np.sort(cost_matrix[row_ind, col_ind]))


def test_linear_sum_assignment_input_validation():
    assert_raises(ValueError, linear_sum_assignment, [1, 2, 3])

    C = [[1, 2, 3], [4, 5, 6]]
    assert_array_equal(linear_sum_assignment(C), linear_sum_assignment(np.asarray(C)))
    # assert_array_equal(linear_sum_assignment(C),
    #                    linear_sum_assignment(matrix(C)))

    I = np.identity(3)
    assert_array_equal(linear_sum_assignment(I.astype(np.bool)), linear_sum_assignment(I))
    assert_raises(ValueError, linear_sum_assignment, I.astype(str))

    I[0][0] = np.nan
    assert_raises(ValueError, linear_sum_assignment, I)

    I = np.identity(3)
    I[1][1] = np.inf
    assert_raises(ValueError, linear_sum_assignment, I)
