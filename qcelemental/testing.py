import sys
import copy
import math
import pprint
import collections

import numpy as np


class _TestComparisonError(Exception):
    """Error when element or nuclide can't be identified."""

    def __init__(self, msg):
        self.message = '\nTestComparisonError: {}\n\n'.format(msg)


def _success(label):
    """Function to print a '*label*...PASSED' line to screen."""

    print(f'\t{label:.<66}PASSED')
    sys.stdout.flush()


def compare_floats(expected,
                   computed,
                   digits,
                   label=None,
                   *,
                   rtol=1.e-16,
                   equal_nan=False,
                   passnone=False,
                   return_message=False,
                   verbose=1):
    """Returns True if two floats or float arrays are element-wise equal within a tolerance.

    Parameters
    ----------
    expected : float or float array-like
        Reference value against which `computed` is compared.
    computed : float or float array-like
        Input value to compare against `expected`.
    digits : int or float
        Absolute tolerance (see formula below), expressed as decimal digits for comparison.
        Values less than one are taken literally rather than as power.
        So `1` means `atol=0.1` and `2` means `atol=0.01` but `0.04` means `atol=0.04`
    label : str, optional
        Label for passed and error messages. Defaults to calling function name.
    rtol : float, optional
        Relative tolerance (see formula below). By default set to zero so `digits` dominates.
    equal_nan : bool, optional
        Passed to np.isclose.
    passnone : bool, optional
        Return True when both expected and computed are None.
    verbose : int, optional
        Print passed message when >=1.

    Returns
    -------
    allclose : bool
        Returns True if `expected` and `computed` are equal within tolerance; False otherwise.
    message : str, optional
        When return_message=True, also return passed or error message.

    Notes
    -----
    Akin to np.allclose.
    Sets rtol to zero to match expected Psi4 behaviour, otherwise measured as:
        absolute(computed - expected) <= (atol + rtol * absolute(expected))

    """
    label = label or sys._getframe().f_back.f_code.co_name
    pass_message = f'\t{label:.<66}PASSED'

    if passnone:
        if expected is None and computed is None:
            if verbose >= 1: _success(label)
            return (True, pass_message) if return_message else True

    try:
        xptd, cptd = np.array(expected, dtype=np.float), np.array(computed, dtype=np.float)
    except Exception:
        return (False, f"""\t{label}: inputs not cast-able to ndarray of np.float.""") if return_message else False

    if xptd.shape != cptd.shape:
        return (False, f"""\t{label}: computed shape ({cptd.shape}) does not match ({xptd.shape})."""
                ) if return_message else False

    if digits >= 1.0:  # formerly, >
        atol = 10.**-digits
        digits1 = digits + 1
        digits_str = f'to {digits} digits'
    else:
        atol = digits
        digits1 = round(-math.log10(digits)) + 2
        digits_str = f'to {digits}'

    isclose = np.isclose(cptd, xptd, rtol=rtol, atol=atol, equal_nan=equal_nan)
    allclose = bool(np.all(isclose))

    if allclose:
        message = pass_message
        if verbose >= 1: _success(label)

    else:
        if xptd.shape == ():
            xptd_str = f'{xptd:.{digits1}f}'
        else:
            xptd_str = np.array_str(xptd, max_line_width=120, precision=12, suppress_small=True)
            xptd_str = '\n'.join('    ' + ln for ln in xptd_str.splitlines())

        if cptd.shape == ():
            cptd_str = f'{cptd:.{digits1}f}'
        else:
            cptd_str = np.array_str(cptd, max_line_width=120, precision=12, suppress_small=True)
            cptd_str = '\n'.join('    ' + ln for ln in cptd_str.splitlines())

        diff = cptd - xptd
        if xptd.shape == ():
            diff_str = f'{diff:.{digits1}f}'
            message = """\t{}: computed value ({}) does not match ({}) {} by difference ({}).""".format(
                label, cptd_str, xptd_str, digits_str, diff_str)
        else:
            diff[isclose] = 0.0
            diff_str = np.array_str(diff, max_line_width=120, precision=12, suppress_small=False)
            diff_str = '\n'.join('    ' + ln for ln in diff_str.splitlines())
            message = """\t{}: computed value does not match {}.\n  Expected:\n{}\n  Observed:\n{}\n  Difference (passed elements are zeroed):\n{}\n""".format(
                label, digits_str, xptd_str, cptd_str, diff_str)

    if return_message:
        return (allclose, message)
    else:
        return allclose


def compare(expected, computed, label=None, *, return_message=False, verbose=1):
    """Returns True if two floats or float arrays are element-wise equal within a tolerance.

    Parameters
    ----------
    expected : float or float array-like
        Reference value against which `computed` is compared.
    computed : float or float array-like
        Input value to compare against `expected`.
    label : str, optional
        Label for passed and error messages. Defaults to calling function name.
    verbose : int, optional
        Print passed message when >=1.

    Returns
    -------
    allclose : bool
        Returns True if `expected` and `computed` are equal; False otherwise.
    message : str, optional
        When return_message=True, also return passed or error message.

    Notes
    -----
    Akin to np.array_equal.

    """
    label = label or sys._getframe().f_back.f_code.co_name
    pass_message = f'\t{label:.<66}PASSED'

    try:
        xptd, cptd = np.array(expected), np.array(computed)
    except Exception:
        return (False, f"""\t{label}: inputs not cast-able to ndarray.""") if return_message else False

    if xptd.shape != cptd.shape:
        return (False, f"""\t{label}: computed shape ({cptd.shape}) does not match ({xptd.shape})."""
                ) if return_message else False

    isclose = np.asarray(xptd == cptd)
    allclose = bool(isclose.all())
    print(xptd, cptd, isclose, allclose)

    if allclose:
        message = pass_message
        if verbose >= 1: _success(label)

    else:
        if xptd.shape == ():
            xptd_str = f'{xptd}'
        else:
            xptd_str = np.array_str(xptd, max_line_width=120, precision=12, suppress_small=True)
            xptd_str = '\n'.join('    ' + ln for ln in xptd_str.splitlines())

        if cptd.shape == ():
            cptd_str = f'{cptd}'
        else:
            cptd_str = np.array_str(cptd, max_line_width=120, precision=12, suppress_small=True)
            cptd_str = '\n'.join('    ' + ln for ln in cptd_str.splitlines())

        try:
            diff = cptd - xptd
        except TypeError:
            diff_str = '(n/a)'
        else:
            if xptd.shape == ():
                diff_str = f'{diff}'
            else:
                diff_str = np.array_str(diff, max_line_width=120, precision=12, suppress_small=False)
                diff_str = '\n'.join('    ' + ln for ln in diff_str.splitlines())

        if xptd.shape == ():
            message = """\t{}: computed value ({}) does not match ({}) by difference ({}).""".format(
                label, cptd_str, xptd_str, diff_str)
        else:
            message = """\t{}: computed value does not match.\n  Expected:\n{}\n  Observed:\n{}\n  Difference:\n{}\n""".format(
                label, xptd_str, cptd_str, diff_str)

    if return_message:
        return (allclose, message)
    else:
        return allclose


def compare_dicts(expected, computed, tol, label, forgive=None, verbose=1):
    """Compares dictionaries `computed` to `expected` using DeepDiff Float
    comparisons made to `tol` significant decimal places. Note that a clean
    DeepDiff returns {}, which evaluates to False, hence the compare_integers.
    Keys in `forgive` may change between `expected` and `computed` without
    triggering failure.

    """
    try:
        import deepdiff
    except ImportError:
        raise ImportError("""Install deepdiff. `conda install deepdiff -c conda-forge` or `pip install deepdiff`""")

    if forgive is None:
        forgive = []
    forgiven = collections.defaultdict(dict)

    ans = deepdiff.DeepDiff(expected, computed, significant_digits=tol, verbose_level=2)

    for category in list(ans):
        for key in list(ans[category]):
            for fg in forgive:
                fgsig = "root['" + fg + "']"
                if key.startswith(fgsig):
                    forgiven[category][key] = ans[category].pop(key)
        if not ans[category]:
            del ans[category]

    clean = not bool(ans)
    if not clean:
        pprint.pprint(ans)
    if verbose >= 2:
        pprint.pprint(forgiven)
    return compare_integers(True, clean, label, verbose=verbose)


def compare_molrecs(expected, computed, tol, label, forgive=None, verbose=1, relative_geoms='exact'):
    """Function to compare Molecule dictionaries. Prints
#    :py:func:`util.success` when elements of `computed` match elements of
#    `expected` to `tol` number of digits (for float arrays).

    """
    thresh = 10**-tol if tol >= 1 else tol

    # Need to manipulate the dictionaries a bit, so hold values
    xptd = copy.deepcopy(expected)
    cptd = copy.deepcopy(computed)

    def massage_dicts(dicary):
        # deepdiff can't cope with np.int type
        #   https://github.com/seperman/deepdiff/issues/97
        if 'elez' in dicary:
            dicary['elez'] = [int(z) for z in dicary['elez']]
        if 'elea' in dicary:
            dicary['elea'] = [int(a) for a in dicary['elea']]
        # deepdiff w/py27 complains about unicode type and val errors
        if 'elem' in dicary:
            dicary['elem'] = [str(e) for e in dicary['elem']]
        if 'elbl' in dicary:
            dicary['elbl'] = [str(l) for l in dicary['elbl']]
        if 'fix_symmetry' in dicary:
            dicary['fix_symmetry'] = str(dicary['fix_symmetry'])
        if 'units' in dicary:
            dicary['units'] = str(dicary['units'])
        if 'fragment_files' in dicary:
            dicary['fragment_files'] = [str(f) for f in dicary['fragment_files']]
        # and about int vs long errors
        if 'molecular_multiplicity' in dicary:
            dicary['molecular_multiplicity'] = int(dicary['molecular_multiplicity'])
        if 'fragment_multiplicities' in dicary:
            dicary['fragment_multiplicities'] = [(m if m is None else int(m))
                                                 for m in dicary['fragment_multiplicities']]
        if 'fragment_separators' in dicary:
            dicary['fragment_separators'] = [(s if s is None else int(s)) for s in dicary['fragment_separators']]
        # forgive generator version changes
        if 'provenance' in dicary:
            dicary['provenance'].pop('version')
        # regularize connectivity ordering
        if 'connectivity' in dicary:
            conn = [(min(at1, at2), max(at1, at2), bo) for (at1, at2, bo) in dicary['connectivity']]
            conn.sort(key=lambda tup: tup[0])
            dicary['connectivity'] = conn

        return dicary

    xptd = massage_dicts(xptd)
    cptd = massage_dicts(cptd)

    if relative_geoms == 'exact':
        pass
    elif relative_geoms == 'align':
        raise FeatureNotImplemented(
            """compare_molrecs(..., relative_geoms='align') not available without B787 from qcdb.""")
        ## can't just expect geometries to match, so we'll align them, check that
        ##   they overlap and that the translation/rotation arrays jibe with
        ##   fix_com/orientation, then attach the oriented geom to computed before the
        ##   recursive dict comparison.
        #from .align import B787
        #cgeom = np.array(cptd['geom']).reshape((-1, 3))
        #rgeom = np.array(xptd['geom']).reshape((-1, 3))
        #rmsd, mill = B787(rgeom=rgeom,
        #                  cgeom=cgeom,
        #                  runiq=None,
        #                  cuniq=None,
        #                  atoms_map=True,
        #                  mols_align=True,
        #                  run_mirror=False,
        #                  verbose=0)
        #if cptd['fix_com']:
        #    compare_integers(1, np.allclose(np.zeros((3)), mill.shift, atol=thresh), 'null shift', verbose=verbose)
        #if cptd['fix_orientation']:
        #    compare_integers(1, np.allclose(np.identity(3), mill.rotation, atol=thresh), 'null rotation', verbose=verbose)
        #ageom = mill.align_coordinates(cgeom)
        #cptd['geom'] = ageom.reshape((-1))

    compare_dicts(xptd, cptd, tol, label, forgive=forgive, verbose=verbose)
