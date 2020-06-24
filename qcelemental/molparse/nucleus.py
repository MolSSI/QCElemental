import re
from functools import lru_cache
from typing import List, Tuple

from ..exceptions import NotAnElementError, ValidationError
from ..periodic_table import periodictable
from .regex import NUCLEUS

_nucleus = re.compile(r"\A" + NUCLEUS + r"\Z", re.IGNORECASE | re.VERBOSE)


@lru_cache(maxsize=512)
def reconcile_nucleus(
    A: int = None,
    Z: int = None,
    E: str = None,
    mass: float = None,
    real: bool = None,
    label: str = None,
    speclabel: bool = True,
    nonphysical: bool = False,
    mtol: float = 1.0e-3,
    verbose: int = 1,
) -> Tuple[int, int, str, float, bool, str]:
    """Forms consistent set of nucleus descriptors from all information
    from arguments, supplemented by the periodic table. At the least,
    must provide element identity somehow. Defaults to most-abundant
    isotope.

    Parameters
    ----------
    A : int, optional
        Mass number, number of protons and neutrons.
    Z : int, optional
        Atomic number, number of protons.
    E : str, optional
        Element symbol from periodic table.
    mass : float, optional
        Atomic mass [u].
    real : bool, optional
        Whether real or ghost/absent.
    label : str, optional
        Atom label according to :py:data:`qcelemental.molparse.regex.NUCLEUS`.
    speclabel : bool, optional
        If `True`, interpret `label` as potentially full nucleus spec including
        ghosting, isotope, mass, tagging information, e.g., ``@13C_mine`` or
        ``He4@4.01``. If `False`, interpret `label` as only the user/tagging
        extension to nucleus label, e.g. ``_mine`` or ``4`` in the previous examples.
    nonphysical : bool, optional
        When `True`, turns off sanity checking that prevents periodic table
        violations (e.g, light uranium: ``1U@1.007``).
    mtol : float, optional
        How different `mass` can be from a known nuclide mass and still
        merit the mass number assignment. Note that for elements dominated
        by a single isotope, the default may not be tight enough to
        prevent standard atomic weight (abundance-average of isotopes)
        from being labeled as the dominant isotope for A.
    verbose : int, optional
        Quantity of printing.

    Returns
    -------
    A, Z, E, mass, real, userlabel : int, int, str, float, bool, str
        mass number, unless clues don't point to a known nuclide, in which case `-1`.
        atomic number.
        element symbol, capitalized.
        mass value [u].
        real/ghost.
        user portion of `label` if present, else ''.

    Raises
    ------
    qcelemental.NotAnElementError
    qcelemental.ValidationError

    Examples
    --------
    >>> reconcile_nucleus(E='co')
    >>> reconcile_nucleus(Z=27)
    >>> reconcile_nucleus(A=59, Z=27)
    >>> reconcile_nucleus(E='cO', mass=58.933195048)
    >>> reconcile_nucleus(A=59, Z=27, E='CO')
    >>> reconcile_nucleus(A=59, E='cO', mass=58.933195048)
    >>> reconcile_nucleus(label='co')
    >>> reconcile_nucleus(label='59co')
    >>> reconcile_nucleus(label='co@58.933195048')
    >>> reconcile_nucleus(A=59, Z=27, E='cO', mass=58.933195048, label='co@58.933195048')
    >>> reconcile_nucleus(A=59, Z=27, E='cO', mass=58.933195048, label='27@58.933195048')
    >>> reconcile_nucleus(label='27')
    59, 27, 'Co', 58.933195048, True, ''

    >>> reconcile_nucleus(label='co_miNe')
    >>> reconcile_nucleus(label='co_mIne@58.933195048')
    59, 27, 'Co', 58.933195048, True, '_mine'

    >>> reconcile_nucleus(E='cO', mass=58.933)
    >>> reconcile_nucleus(label='cO@58.933')
    59, 27, 'Co', 58.933, True, ''
    >>> assert 59, 27, 'Co', 58.933, True, '' == reconcile_nucleus(E='cO', mass=58.933, mtol=1.e-4))
    AssertionError

    >>> reconcile_nucleus(E='Co', A=60)
    >>> reconcile_nucleus(Z=27, A=60, real=True)
    >>> reconcile_nucleus(E='Co', A=60)
    >>> reconcile_nucleus(Z=27, mass=59.933817059)
    >>> reconcile_nucleus(A=60, Z=27, mass=59.933817059)
    >>> reconcile_nucleus(label='60Co')
    >>> reconcile_nucleus(label='27', mass=59.933817059)
    >>> reconcile_nucleus(label='Co', mass=59.933817059)
    >>> reconcile_nucleus(A=60, label='Co')
    60, 27, 'Co', 59.933817059, True, ''

    >>> reconcile_nucleus(E='Co', A=60, real=False))
    >>> reconcile_nucleus(A=60, Z=27, mass=59.933817059, real=0))
    >>> reconcile_nucleus(label='@60Co'))
    >>> reconcile_nucleus(label='Gh(27)', mass=59.933817059))
    >>> reconcile_nucleus(label='@Co', mass=59.933817059))
    >>> reconcile_nucleus(A=60, label='Gh(Co)'))
    60, 27, 'Co', 59.933817059, False, ''

    >>> reconcile_nucleus(Z=27, mass=200, nonphysical=True)
    60, 27, 'Co', 200.00000000, True, ''

    >>> reconcile_nucleus(mass=60.6, Z=27)
    >>> reconcile_nucleus(mass=60.6, E='Co')
    >>> reconcile_nucleus(mass=60.6, label='27')
    >>> reconcile_nucleus(label='Co@60.6')
    -1, 27, 'Co', 60.6, True, ''

    >>> reconcile_nucleus(mass=60.6, Z=27, A=61))
    >>> reconcile_nucleus(A=80, Z=27)
    >>> reconcile_nucleus(Z=27, mass=200)
    >>> reconcile_nucleus(Z=27, mass=-200, nonphysical=True)
    >>> reconcile_nucleus(Z=-27, mass=200, nonphysical=True)
    >>> reconcile_nucleus(Z=1, label='he')
    >>> reconcile_nucleus(A=4, label='3he')
    >>> reconcile_nucleus(label='@U', real=True)
    >>> reconcile_nucleus(label='U', real=False)
    ValidationError

    """

    # <<< define functions
    log_text = verbose >= 2

    def reconcile(exact, tests, feature):
        """Returns a member from `exact` that passes all `tests`, else raises error for `feature`."""

        for candidate in exact:
            assessment = [fn(candidate) for fn in tests]
            if log_text:
                text.append(
                    """Assess {} candidate {}: {} --> {}""".format(feature, candidate, assessment, all(assessment))
                )
            if all(assessment):
                return candidate

        err = """Inconsistent or unspecified {}: A: {}, Z: {}, E: {}, mass: {}, real: {}, label: {}""".format(
            feature, A, Z, E, mass, real, label
        )
        if verbose > -1:
            print("\n\n" + "\n".join(text))
        raise ValidationError(err)

    def offer_element_symbol(e):
        """Given an element, what can be suggested and asserted about Z, A, mass?"""

        _Z = periodictable.to_Z(e, strict=True)
        offer_atomic_number(_Z)

    def offer_atomic_number(z):
        """Given an atomic number, what can be suggested and asserted about Z, A, mass?"""

        z = int(z)

        z_symbol = periodictable.to_E(z)
        z_mass = periodictable.to_mass(z)
        z_a = periodictable.to_A(z)

        z_a2mass = periodictable._el2a2mass[z_symbol]
        z_a2mass_min = min(z_a2mass.keys())
        z_a2mass_max = max(z_a2mass.keys())
        z_mass2a_min = min(z_a2mass.values())
        z_mass2a_max = max(z_a2mass.values())

        Z_exact.append(z)
        Z_range.append(lambda x, z=z: x == z)

        A_exact.append(z_a)
        if nonphysical:
            A_range.append(lambda x: x == -1 or x >= 1)
            if log_text:
                text.append("""For A, input Z: {}, requires 1 < A or -1, nonphysical""".format(z))
        else:
            A_range.append(lambda x, amin=z_a2mass_min, amax=z_a2mass_max: x == -1 or (x >= amin and x <= amax))
            if log_text:
                text.append(
                    """For A, input Z: {} requires {} < A < {} or -1, the known mass number range for element""".format(
                        z, z_a2mass_min, z_a2mass_max
                    )
                )

        m_exact.append(z_mass)
        if nonphysical:
            m_range.append(lambda x: x > 0.5)
            if log_text:
                text.append("""For mass, input Z: {}, requires 0.5 < mass, nonphysical""".format(z))
        else:
            m_range.append(lambda x, mmin=z_mass2a_min, mmax=z_mass2a_max: x >= mmin - mmtol and x <= mmax + mmtol)
            if log_text:
                text.append(
                    """For mass, input Z: {} requires {} < mass < {} +/-{}, the known mass range for element""".format(
                        z, z_mass2a_min, z_mass2a_max, mmtol
                    )
                )

    def offer_mass_number(z, a):
        """Given a mass number and element, what can be suggested and asserted about A, mass?"""

        a = int(a)
        a_eliso = periodictable.to_E(z) + str(a)
        a_mass = periodictable.to_mass(a_eliso)

        A_exact.append(a)
        A_range.append(lambda x, a=a: x == a)
        if log_text:
            text.append("""For A, inputs Z: {}, A: {} require A == {}.""".format(z, a, a))

        m_exact.append(a_mass)
        m_range.append(lambda x, a_mass=a_mass: abs(x - a_mass) < mtol)
        if log_text:
            text.append("""For mass, inputs Z: {}, A: {} require abs(mass - {}) < {}""".format(z, a, a_mass, mtol))

    def offer_mass_value(z, m):
        """Given a mass and element, what can be suggested and asserted about A, mass?"""

        m = float(m)
        m_a = int(round(m, 0))
        m_eliso = periodictable.to_E(z) + str(m_a)

        try:
            if abs(periodictable.to_mass(m_eliso) - m) > mtol:
                # only offer A if known nuclide. C@12.4 != 12C
                m_a = -1
        except NotAnElementError:
            m_a = -1

        A_exact.append(m_a)
        A_range.append(lambda x, m_a=m_a: x == m_a)
        if log_text:
            text.append("""For A, inputs Z: {}, m: {} require A == {}""".format(z, m, m_a))

        m_exact.append(m)
        m_range.append(lambda x, m=m: x == m)
        if log_text:
            text.append("""For mass, inputs Z: {}, m: {} require m == {}""".format(z, m, m))

    def offer_reality(rgh):
        r_exact.append(rgh)
        r_range.append(lambda x, rgh=rgh: x == rgh)
        if log_text:
            text.append("""For real/ghost, input rgh: {} requires rgh == {}""".format(rgh, rgh))

    def offer_user_label(lbl):
        lbl = str(lbl).lower()
        l_exact.append(lbl)
        l_range.append(lambda x, lbl=lbl: x == lbl)
        if log_text:
            text.append("""For user label, input lbl: {} requires lbl == {}""".format(lbl, lbl))

    # <<< initialize

    text = ["", """--> Inp: A={}, Z={}, E={}, mass={}, real={}, label={}""".format(A, Z, E, mass, real, label)]

    Z_exact: List = []  # *_exact are candidates for the final value
    Z_range: List = []  # *_range are tests that the final value must pass to be valid
    A_exact: List = []
    A_range: List = []
    m_exact: List = []
    m_range: List = []

    r_exact = [True]  # default real/ghost is real
    r_range: List = []
    l_exact = [""]  # default user label is empty string
    l_range: List = []
    mmtol = 0.5  # tolerance for mass outside known masses for element

    # <<< collect evidence for Z/A/m, then reconcile Z

    if Z is not None:
        offer_atomic_number(Z)

    if E is not None:
        offer_element_symbol(E)

    if label is not None and speclabel is True:
        lbl_A, lbl_Z, lbl_E, lbl_mass, lbl_real, lbl_user = parse_nucleus_label(label)

        if lbl_Z is not None:
            offer_atomic_number(lbl_Z)
        if lbl_E is not None:
            offer_element_symbol(lbl_E)

    Z_final = reconcile(Z_exact, Z_range, "atomic number")
    E_final = periodictable.to_E(Z_final)

    # <<< collect more evidence for A/m, then reconcile them

    if A is not None:
        offer_mass_number(Z_final, A)

    if mass is not None:
        offer_mass_value(Z_final, mass)

    if real is not None:
        offer_reality(real)

    if label is not None:
        if speclabel:
            offer_reality(lbl_real)
            if lbl_A is not None:
                offer_mass_number(Z_final, lbl_A)
            if lbl_mass is not None:
                offer_mass_value(Z_final, lbl_mass)
            if lbl_user is not None:
                offer_user_label(lbl_user)
        else:
            offer_user_label(label)

    mass_final = reconcile(m_exact, m_range, "mass")
    A_final = reconcile(A_exact, A_range, "mass number")
    real_final = reconcile(r_exact, r_range, "real/ghost")
    user_final = reconcile(l_exact, l_range, "user label")

    if log_text:
        text.append(
            """<-- Out: A={}, Z={}, E={}, mass={}, real={}, user={}""".format(
                A_final, Z_final, E_final, mass_final, real_final, user_final
            )
        )

    if log_text:
        print("\n".join(text))

    return (A_final, Z_final, E_final, mass_final, real_final, user_final)


def parse_nucleus_label(label):
    """Separate molecule nucleus string into fields.

    Parameters
    ----------
    label : str
        Conveys at least element and ghostedness and possibly isotope, mass, and
        user info in accordance with :py:data:`qcelemental.molparse.regex.NUCLEUS`.

    Returns
    -------
    A, Z, E, mass, real, user : int or None, int or None, str or None, float or None, bool, str or None
        Field breakdown of `label`.

    Raises
    ------
    qcelemental.ValidationError
        If `label` does not match NUCLEUS.

    Examples
    --------
    >>> parse_nucleus_label('@ca_miNe')
    None, None, 'ca', None False, '_miNe'

    >>> parse_nucleus_label('Gh(Ca_mine)')
    None, None, 'Ca', None '_mine', False

    >>> parse_nucleus_label('@Ca_mine@1.07')
    None, None, 'Ca', 1.07 False, '_mine'

    >>> parse_nucleus_label('Gh(cA_MINE@1.07)')
    None, None, 'cA', 1.07 False, '_MINE'

    >>> parse_nucleus_label('@40Ca_mine@1.07')
    40, None, 'Ca', 1.07 False, '_mine'

    >>> parse_nucleus_label('Gh(40Ca_mine@1.07)')
    40, None, 'Ca', 1.07 False, '_mine'

    >>> parse_nucleus_label('444lu333@4.0')
    444, None, 'lu', 4.0 True, '333'

    >>> parse_nucleus_label('@444lu333@4.4')
    444, None, 'lu', 4.4 False, '333'

    >>> parse_nucleus_label('8i')
    8, None, 'i', None True, None

    >>> parse_nucleus_label('53_mI4')
    None, 53, None, None True, '_mI4'

    >>> parse_nucleus_label('@5_MINEs3@4.4')
    None, 5, None, 4.4 False, '_MINEs3'

    >>> parse_nucleus_label('Gh(555_mines3@0.1)')
    None, 555, None, 0.1 False, '_mines3'

    """
    matchobj = _nucleus.match(label)

    if matchobj:
        real = not (matchobj.group("gh1") or matchobj.group("gh2"))

        if matchobj.group("A"):
            A = int(matchobj.group("A"))
        else:
            A = None

        if matchobj.group("Z"):
            Z = int(matchobj.group("Z"))
        else:
            Z = None

        E = matchobj.group("E")

        if matchobj.group("user1"):
            user = matchobj.group("user1")
        elif matchobj.group("user2"):
            user = matchobj.group("user2")
        else:
            user = None

        if matchobj.group("mass"):
            mass = float(matchobj.group("mass"))
        else:
            mass = None
    else:
        raise ValidationError("""Nucleus label is not parseable: {}""".format(label))

    return A, Z, E, mass, real, user
