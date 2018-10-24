import sys

import utils_compare


def true_false_decorator(compare_fn, *args, **kwargs):
    """Turns `compare_fn` that returns `None` on success and raises
    `_TestComparisonError` on failure into a function that returns
    True/False, suitable for assertions in pytest.

    """

    def true_false_wrapper(*args, **kwargs):
        try:
            compare_fn(*args, **kwargs)
        except utils_compare._TestComparisonError as err:
            return False
        else:
            return True

    return true_false_wrapper


compare_values = true_false_decorator(utils_compare.compare_values)
compare_strings = true_false_decorator(utils_compare.compare_strings)
compare_integers = true_false_decorator(utils_compare.compare_integers)
#compare_matrices = true_false_decorator(utils_compare.compare_matrices)
#compare_arrays = true_false_decorator(utils_compare.compare_arrays)
compare_dicts = true_false_decorator(utils_compare.compare_dicts)
compare_molrecs = true_false_decorator(utils_compare.compare_molrecs)


def tnm():
    """Returns the name of the calling function, usually name of test case."""

    return sys._getframe().f_back.f_code.co_name
