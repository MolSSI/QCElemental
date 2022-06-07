import copy
import logging
import pprint
import sys
from typing import Callable, Dict, List, Tuple, Union

import numpy as np
from pydantic import BaseModel

from qcelemental.models.basemodels import ProtoModel

pp = pprint.PrettyPrinter(width=120)


def _handle_return(passfail: bool, label: str, message: str, return_message: bool, quiet: bool = False):
    """Function to print a '*label*...PASSED' line to log."""

    if not quiet:
        if passfail:
            logging.info(f"    {label:.<53}PASSED")
        else:
            logging.error(f"    {label:.<53}FAILED")
            logging.error(f"    {message:.<53}")

    if return_message:
        return passfail, message
    else:
        return passfail


def tnm() -> str:
    """Returns the name of the calling function, usually name of test case."""

    return sys._getframe().f_back.f_code.co_name


def compare_values(
    expected: Union[float, List, np.ndarray],
    computed: Union[float, List, np.ndarray],
    label: str = None,
    *,
    atol: float = 1.0e-6,
    rtol: float = 1.0e-16,
    equal_nan: bool = False,
    equal_phase: bool = False,
    passnone: bool = False,
    quiet: bool = False,
    return_message: bool = False,
    return_handler: Callable = None,
) -> Union[bool, Tuple[bool, str]]:
    r"""Returns True if two floats or float arrays are element-wise equal within a tolerance.

    Parameters
    ----------
    expected
        float or float array-like
        Reference value against which `computed` is compared.
    computed
        float or float array-like
        Input value to compare against `expected`.
    atol
        Absolute tolerance (see formula below).
    label
        Label for passed and error messages. Defaults to calling function name.
    rtol
        Relative tolerance (see formula below). By default set to zero so `atol` dominates.
    equal_nan
        Passed to :func:`numpy.isclose`. Compare NaN's as equal.
    equal_phase
        Compare computed *or its opposite* as equal.
    passnone
        Return True when both expected and computed are None.
    quiet
        Whether to log the return message.
    return_message
        Whether to return tuple. See below.

    Returns
    -------
    allclose : bool
        Returns True if `expected` and `computed` are equal within tolerance; False otherwise.
    message : str
        When return_message=True, also return passed or error message.

    Other Parameters
    ----------------
    return_handler
        Function to control printing, logging, raising, and returning.
        Specialized interception for interfacing testing systems.

    Notes
    -----
    * Akin to :func:`numpy.allclose`.
    * For scalar float-comparable types and for arbitrary-dimension, np.ndarray-castable, uniform-type,
      float-comparable types. For mixed types, use :py:func:`compare_recursive`.
    * Sets rtol to zero to match expected Psi4 behaviour, otherwise measured as:

    .. code-block:: python

        absolute(computed - expected) <= (atol + rtol * absolute(expected))

    """
    label = label or sys._getframe().f_back.f_code.co_name
    pass_message = f"\t{label:.<66}PASSED"
    if return_handler is None:
        return_handler = _handle_return

    if passnone:
        if expected is None and computed is None:
            return return_handler(True, label, pass_message, return_message, quiet)

    if np.iscomplexobj(expected):
        dtype = np.complex
    else:
        dtype = float

    try:
        xptd, cptd = np.array(expected, dtype=dtype), np.array(computed, dtype=dtype)
    except Exception:
        return return_handler(
            False, label, f"""\t{label}: inputs not cast-able to ndarray of {dtype}.""", return_message, quiet
        )

    if xptd.shape != cptd.shape:
        return return_handler(
            False,
            label,
            f"""\t{label}: computed shape ({cptd.shape}) does not match ({xptd.shape}).""",
            return_message,
            quiet,
        )  # lgtm: [py/syntax-error]

    digits1 = abs(int(np.log10(atol))) + 2
    digits_str = f"to atol={atol}"
    if rtol > 1.0e-12:
        digits_str += f", rtol={rtol}"

    isclose = np.isclose(cptd, xptd, rtol=rtol, atol=atol, equal_nan=equal_nan)
    allclose = bool(np.all(isclose))

    if not allclose and equal_phase and hasattr(cptd, "__neg__"):
        n_isclose = np.isclose(-cptd, xptd, rtol=rtol, atol=atol, equal_nan=equal_nan)
        allclose = bool(np.all(n_isclose))

    if allclose:
        message = pass_message

    else:
        if xptd.shape == ():
            xptd_str = f"{float(xptd):.{digits1}f}"
        else:
            xptd_str = np.array_str(xptd, max_line_width=120, precision=12, suppress_small=True)
            xptd_str = "\n".join("    " + ln for ln in xptd_str.splitlines())

        if cptd.shape == ():
            cptd_str = f"{float(cptd):.{digits1}f}"
        else:
            cptd_str = np.array_str(cptd, max_line_width=120, precision=12, suppress_small=True)
            cptd_str = "\n".join("    " + ln for ln in cptd_str.splitlines())

        diff = cptd - xptd
        if xptd.shape == ():
            diff_str = f"{float(diff):.{digits1}f}"
            message = """\t{}: computed value ({}) does not match ({}) {} by difference ({}).""".format(
                label, cptd_str, xptd_str, digits_str, diff_str
            )
        else:
            diff[isclose] = 0.0
            diff_str = np.array_str(diff, max_line_width=120, precision=12, suppress_small=False)
            diff_str = "\n".join("    " + ln for ln in diff_str.splitlines())
            with np.errstate(divide="ignore", invalid="ignore"):
                diffrel = np.divide(diff, xptd)
            np.nan_to_num(diffrel, copy=False)
            diffraw = cptd - xptd
            digits_str += f" (o-e: RMS {_rms(diffraw):.1e}, MAX {np.amax(np.absolute(diffraw)):.1e}, RMAX {np.amax(np.absolute(diffrel)):.1e})"
            message = """\t{}: computed value does not match {}.\n  Expected:\n{}\n  Observed:\n{}\n  Difference (passed elements are zeroed):\n{}\n""".format(
                label, digits_str, xptd_str, cptd_str, diff_str
            )

    return return_handler(allclose, label, message, return_message, quiet)


def _rms(arr: np.ndarray) -> float:
    return np.sqrt(np.mean(np.square(arr)))


def compare(
    expected: Union[int, bool, str, List[int], np.ndarray],
    computed: Union[int, bool, str, List[int], np.ndarray],
    label: str = None,
    *,
    equal_phase: bool = False,
    quiet: bool = False,
    return_message: bool = False,
    return_handler: Callable = None,
) -> Union[bool, Tuple[bool, str]]:
    r"""Returns True if two integers, strings, booleans, or integer arrays are element-wise equal.

    Parameters
    ----------
    expected
        int, bool, str or array-like of same.
        Reference value against which `computed` is compared.
    computed
        int, bool, str or array-like of same.
        Input value to compare against `expected`.
    label
        Label for passed and error messages. Defaults to calling function name.
    equal_phase
        Compare computed *or its opposite* as equal.
    quiet
        Whether to log the return message.
    return_message
        Whether to return tuple. See below.

    Returns
    -------
    allclose : bool
        Returns True if `expected` and `computed` are equal; False otherwise.
    message : str
        When return_message=True, also return passed or error message.

    Other Parameters
    ----------------
    return_handler
        Function to control printing, logging, raising, and returning.
        Specialized interception for interfacing testing systems.

    Notes
    -----
    * Akin to :func:`numpy.array_equal`.
    * For scalar exactly-comparable types and for arbitrary-dimension, np.ndarray-castable, uniform-type,
      exactly-comparable types. For mixed types, use :py:func:`compare_recursive`.

    """
    label = label or sys._getframe().f_back.f_code.co_name
    pass_message = f"\t{label:.<66}PASSED"
    if return_handler is None:
        return_handler = _handle_return

    try:
        xptd, cptd = np.array(expected), np.array(computed)
    except Exception:
        return return_handler(False, label, f"""\t{label}: inputs not cast-able to ndarray.""", return_message, quiet)

    if xptd.shape != cptd.shape:
        return return_handler(
            False,
            label,
            f"""\t{label}: computed shape ({cptd.shape}) does not match ({xptd.shape}).""",
            return_message,
            quiet,
        )

    isclose = np.asarray(xptd == cptd)
    allclose = bool(isclose.all())

    if not allclose and equal_phase:
        try:
            n_isclose = np.asarray(xptd == -cptd)
        except TypeError:
            pass
        else:
            allclose = bool(n_isclose.all())

    if allclose:
        message = pass_message

    else:
        if xptd.shape == ():
            xptd_str = f"{xptd}"
        else:
            xptd_str = np.array_str(xptd, max_line_width=120, precision=12, suppress_small=True)
            xptd_str = "\n".join("    " + ln for ln in xptd_str.splitlines())

        if cptd.shape == ():
            cptd_str = f"{cptd}"
        else:
            cptd_str = np.array_str(cptd, max_line_width=120, precision=12, suppress_small=True)
            cptd_str = "\n".join("    " + ln for ln in cptd_str.splitlines())

        try:
            diff = cptd - xptd
        except TypeError:
            diff_str = "(n/a)"
        else:
            if xptd.shape == ():
                diff_str = f"{diff}"
            else:
                diff_str = np.array_str(diff, max_line_width=120, precision=12, suppress_small=False)
                diff_str = "\n".join("    " + ln for ln in diff_str.splitlines())

        if xptd.shape == ():
            message = """\t{}: computed value ({}) does not match ({}) by difference ({}).""".format(
                label, cptd_str, xptd_str, diff_str
            )
        else:
            message = """\t{}: computed value does not match.\n  Expected:\n{}\n  Observed:\n{}\n  Difference:\n{}\n""".format(
                label, xptd_str, cptd_str, diff_str
            )

    return return_handler(allclose, label, message, return_message, quiet)


def _compare_recursive(expected, computed, atol, rtol, _prefix=False, equal_phase=False):

    errors = []
    name = _prefix or "root"
    prefix = name + "."

    # Initial conversions if required
    if isinstance(expected, BaseModel):
        expected = expected.dict()

    if isinstance(computed, BaseModel):
        computed = computed.dict()

    if isinstance(expected, (str, int, bool, complex)):
        if expected != computed:
            errors.append((name, "Value {} did not match {}.".format(expected, computed)))

    elif isinstance(expected, (list, tuple)):
        try:
            if len(expected) != len(computed):
                errors.append((name, "Iterable lengths did not match"))
            else:
                for i, item1, item2 in zip(range(len(expected)), expected, computed):
                    errors.extend(
                        _compare_recursive(
                            item1, item2, _prefix=prefix + str(i), atol=atol, rtol=rtol, equal_phase=equal_phase
                        )
                    )
        except TypeError:
            errors.append((name, "Expected computed to have a __len__()"))

    elif isinstance(expected, dict):
        expected_extra = computed.keys() - expected.keys()
        computed_extra = expected.keys() - computed.keys()
        if len(expected_extra):
            errors.append((name, "Found extra keys {}".format(expected_extra)))
        if len(computed_extra):
            errors.append((name, "Missing keys {}".format(computed_extra)))

        for k in expected.keys() & computed.keys():
            name = prefix + str(k)
            errors.extend(
                _compare_recursive(
                    expected[k], computed[k], _prefix=name, atol=atol, rtol=rtol, equal_phase=equal_phase
                )
            )

    elif isinstance(expected, (float, np.number)):
        passfail, msg = compare_values(
            expected, computed, atol=atol, rtol=rtol, equal_phase=equal_phase, return_message=True, quiet=True
        )
        if not passfail:
            errors.append((name, "Arrays differ." + msg))

    elif isinstance(expected, np.ndarray):
        if np.issubdtype(expected.dtype, np.floating):
            passfail, msg = compare_values(
                expected, computed, atol=atol, rtol=rtol, equal_phase=equal_phase, return_message=True, quiet=True
            )
        else:
            passfail, msg = compare(expected, computed, equal_phase=equal_phase, return_message=True, quiet=True)
        if not passfail:
            errors.append((name, "Arrays differ." + msg))

    elif isinstance(expected, type(None)):
        if expected is not computed:
            errors.append((name, "'None' does not match."))

    else:
        errors.append((name, f"Type {type(expected)} not understood -- stopping recursive compare."))

    return errors


def compare_recursive(
    expected: Union[Dict, BaseModel, "ProtoModel"],  # type: ignore
    computed: Union[Dict, BaseModel, "ProtoModel"],  # type: ignore
    label: str = None,
    *,
    atol: float = 1.0e-6,
    rtol: float = 1.0e-16,
    forgive: List[str] = None,
    equal_phase: Union[bool, List] = False,
    quiet: bool = False,
    return_message: bool = False,
    return_handler: Callable = None,
) -> Union[bool, Tuple[bool, str]]:
    r"""
    Recursively compares nested structures such as dictionaries and lists.

    Parameters
    ----------
    expected
        Reference value against which `computed` is compared.
        Dict may be of any depth but should contain Plain Old Data.
    computed
        Input value to compare against `expected`.
        Dict may be of any depth but should contain Plain Old Data.
    atol
        Absolute tolerance (see formula below).
    label
        Label for passed and error messages. Defaults to calling function name.
    rtol
        Relative tolerance (see formula below). By default set to zero so `atol` dominates.
    forgive
        Keys in top level which may change between `expected` and `computed` without triggering failure.
    equal_phase
        Compare computed *or its opposite* as equal.
    quiet
        Whether to log the return message.
    return_message
        Whether to return tuple. See below.

    Returns
    -------
    allclose : bool
        Returns True if `expected` and `computed` are equal within tolerance; False otherwise.
    message : str
        When return_message=True, also return passed or error message.

    Notes
    -----

    .. code-block:: python

        absolute(computed - expected) <= (atol + rtol * absolute(expected))

    """
    label = label or sys._getframe().f_back.f_code.co_name
    if atol >= 1:
        raise ValueError(
            "Prior to v0.4.0, ``compare_recursive`` used to 10**-atol any atol >=1. That has ceased, so please express your atol literally."
        )
    if return_handler is None:
        return_handler = _handle_return

    errors = _compare_recursive(expected, computed, atol=atol, rtol=rtol)

    if errors and equal_phase:
        n_errors = _compare_recursive(expected, computed, atol=atol, rtol=rtol, equal_phase=True)
        n_errors = dict(n_errors)

        if equal_phase is False:
            equal_phase = []
        elif equal_phase is True:
            equal_phase = list(dict(errors).keys())
        else:
            equal_phase = [(ep if ep.startswith("root.") else "root." + ep) for ep in equal_phase]
        phased = []

        for nomatch in sorted(errors):
            for ep in equal_phase or []:
                if nomatch[0].startswith(ep):
                    if nomatch[0] not in n_errors:
                        phased.append(nomatch)
                        errors.remove(nomatch)

    if forgive is None:
        forgive = []
    else:
        forgive = [(fg if fg.startswith("root.") else "root." + fg) for fg in forgive]
    forgiven = []

    for nomatch in sorted(errors):
        for fg in forgive or []:
            if nomatch[0].startswith(fg):
                forgiven.append(nomatch)
                errors.remove(nomatch)

    ## print if verbose >= 2 if these functions had that knob
    # forgiven_message = []
    # for e in sorted(forgiven):
    #     forgiven_message.append(e[0])
    #     forgiven_message.append("forgiven    " + e[1])
    # pprint.pprint(forgiven)

    message = []
    for e in sorted(errors):
        message.append(e[0])
        message.append("    " + e[1])

    ret_msg_str = "\n".join(message)

    return return_handler(len(ret_msg_str) == 0, label, ret_msg_str, return_message, quiet)


def compare_molrecs(
    expected,
    computed,
    label: str = None,
    *,
    atol: float = 1.0e-6,
    rtol: float = 1.0e-16,
    forgive=None,
    verbose: int = 1,
    relative_geoms="exact",
    return_message: bool = False,
    return_handler: Callable = None,
) -> bool:
    """Function to compare Molecule dictionaries."""
    # Need to manipulate the dictionaries a bit, so hold values
    xptd = copy.deepcopy(expected)
    cptd = copy.deepcopy(computed)

    def massage_dicts(dicary):
        # if 'fix_symmetry' in dicary:
        #     dicary['fix_symmetry'] = str(dicary['fix_symmetry'])
        # if 'units' in dicary:
        #     dicary['units'] = str(dicary['units'])
        if "fragment_files" in dicary:
            dicary["fragment_files"] = [str(f) for f in dicary["fragment_files"]]
        # and about int vs long errors
        # if 'molecular_multiplicity' in dicary:
        #     dicary['molecular_multiplicity'] = int(dicary['molecular_multiplicity'])
        # if 'fragment_multiplicities' in dicary:
        #     dicary['fragment_multiplicities'] = [(m if m is None else int(m))
        #                                          for m in dicary['fragment_multiplicities']]
        if "fragment_separators" in dicary:
            dicary["fragment_separators"] = [(s if s is None else int(s)) for s in dicary["fragment_separators"]]
        # forgive generator version changes
        if "provenance" in dicary:
            dicary["provenance"].pop("version")
        # regularize connectivity ordering
        if "connectivity" in dicary:
            conn = [(min(at1, at2), max(at1, at2), bo) for (at1, at2, bo) in dicary["connectivity"]]
            conn.sort(key=lambda tup: tup[0])
            dicary["connectivity"] = conn

        return dicary

    xptd = massage_dicts(xptd)
    cptd = massage_dicts(cptd)

    if relative_geoms == "exact":
        pass
    elif relative_geoms == "align":
        # can't just expect geometries to match, so we'll align them, check that
        #   they overlap and that the translation/rotation arrays jibe with
        #   fix_com/orientation, then attach the oriented geom to computed before the
        #   recursive dict comparison.
        from .molutil.align import B787

        cgeom = np.array(cptd["geom"]).reshape((-1, 3))
        rgeom = np.array(xptd["geom"]).reshape((-1, 3))
        rmsd, mill = B787(
            rgeom=rgeom,
            cgeom=cgeom,
            runiq=None,
            cuniq=None,
            atoms_map=True,
            mols_align=True,
            run_mirror=False,
            verbose=0,
        )
        if cptd["fix_com"]:
            return compare(
                True,
                np.allclose(np.zeros((3)), mill.shift, atol=atol),
                "null shift",
                quiet=(verbose == 0),
                return_message=return_message,
                return_handler=return_handler,
            )
        if cptd["fix_orientation"]:
            return compare(
                True,
                np.allclose(np.identity(3), mill.rotation, atol=atol),
                "null rotation",
                quiet=(verbose == 0),
                return_message=return_message,
                return_handler=return_handler,
            )
        ageom = mill.align_coordinates(cgeom)
        cptd["geom"] = ageom.reshape((-1))

    return compare_recursive(
        xptd,
        cptd,
        atol=atol,
        rtol=rtol,
        label=label,
        forgive=forgive,
        quiet=(verbose == 0),
        return_message=return_message,
        return_handler=return_handler,
    )
