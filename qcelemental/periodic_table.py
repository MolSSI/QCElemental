"""
Periodic table class
"""

import collections
from decimal import Decimal
from typing import Union

from .exceptions import NotAnElementError


class PeriodicTable:
    """Nuclear and mass data about chemical elements from NIST.

    Parameters
    ----------
    None

    Attributes
    ----------
    A : list of int
        Mass number, number of protons and neutrons, starting with 0 for dummies.
    Z : list of int
        Atomic number, number of protons, starting with 0 for dummies.
    E : list of str
        Element symbol from periodic table, starting with "X" for dummies. "Fe" capitalization.
    EA : list of str
        Nuclide symbol in E + A form, e.g., "Li6".
        List `EA` is a superset of `E`; that is, both "Li6" and "Li" present.
        For hydrogen, "D" and "T" also included.
    mass : list of :py:class:`decimal.Decimal`
        Atomic mass [u].
        For nuclides (e.g., "Li6"), the reported mass.
        For stable elements (e.g., "Li"), the mass of the most abundant isotope ("Li7").
        For unstable elements (e.g., "Pu"), the mass of the longest-lived isotope ("Pu244").
    name : list of str
        Element name from periodic table, starting with "Dummy". "Iron" capitalization.

    """

    def __init__(self):

        from . import data

        # Of length number of elements
        self.Z = data.nist_2011_atomic_weights["Z"]
        self.E = data.nist_2011_atomic_weights["E"]
        self.name = data.nist_2011_atomic_weights["name"]

        self._el2z = dict(zip(self.E, self.Z))
        self._z2el = collections.OrderedDict(zip(self.Z, self.E))
        self._element2el = dict(zip(self.name, self.E))
        self._el2element = dict(zip(self.E, self.name))

        # Of length number of isotopes
        self._EE = data.nist_2011_atomic_weights["_EE"]
        self.EA = data.nist_2011_atomic_weights["EA"]
        self.A = data.nist_2011_atomic_weights["A"]
        self.mass = data.nist_2011_atomic_weights["mass"]

        self._eliso2mass = dict(zip(self.EA, self.mass))
        self._eliso2el = dict(zip(self.EA, self._EE))
        self._eliso2a = dict(zip(self.EA, self.A))
        self._el2a2mass = collections.defaultdict(dict)
        for EE, m, A in zip(self._EE, self.mass, self.A):
            self._el2a2mass[EE][A] = float(m)

    def _resolve_atom_to_key(self, atom: Union[int, str], strict: bool = False) -> str:
        """Given `atom` as element name, element symbol, nuclide symbol, atomic number, or atomic number string,
        return valid `self._eliso2mass` key, regardless of case. Raises `NotAnElementError` if unidentifiable.

        """

        def resolve_eliso(atom):
            try:
                self._eliso2mass[atom.capitalize()]  # type: ignore
            except (KeyError, AttributeError):
                try:
                    E = self._z2el[int(atom)]
                except (KeyError, ValueError):
                    try:
                        E = self._element2el[atom.capitalize()]  # type: ignore
                    except (KeyError, AttributeError):
                        raise NotAnElementError(atom)
                    else:
                        return E
                else:
                    return E
            else:
                assert isinstance(atom, str)
                return atom.capitalize()

        eliso = resolve_eliso(atom)

        if strict and eliso not in self.E:
            raise NotAnElementError(eliso, strict=strict)

        return eliso

    def to_mass(self, atom: Union[int, str], *, return_decimal: bool = False) -> Union[float, "Decimal"]:
        """Get atomic mass of `atom`.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.
        return_decimal : bool, optional
            Whether to preserve significant figures information by returning as Decimal (`True`) or to convert to float (`False`).

        Returns
        -------
        decimal.Decimal or float
            Atomic mass [u]. See above for type.
            If `atom` is nuclide (e.g., "Li6"), the reported mass.
            If `atom` is stable element (e.g., "Li"), the mass of the most abundant isotope, "Li7".
            If `atom` is unstable element (e.g., "Pu"), the mass of the longest-lived isotope, "Pu244".

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.

        """
        identifier = self._resolve_atom_to_key(atom)
        mass = self._eliso2mass[identifier]

        if return_decimal:
            return Decimal(mass)
        else:
            return float(mass)

    def to_A(self, atom: Union[int, str]) -> int:
        """Get mass number of `atom`.

        Functions :py:func:`to_A` and :py:func:`to_mass_number` are aliases.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.

        Returns
        -------
        int
            Mass number, number of protons and neutrons.
            If `atom` is nuclide (e.g., "Li6"), the corresponding mass number, 6.
            If `atom` is stable element (e.g., "Li"), the mass number of the most abundant isotope, 7.
            If `atom` is unstable element (e.g., "Pu"), the mass number of the longest-lived isotope, 244.

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.

        """
        identifier = self._resolve_atom_to_key(atom)
        return self._eliso2a[identifier]

    def to_Z(self, atom: Union[int, str], strict: bool = False) -> int:
        """Get atomic number of `atom`.

        Functions :py:func:`to_Z` and :py:func:`to_atomic_number` are aliases.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.
        strict
            Allow only element identification in `atom`, not nuclide.

        Returns
        -------
        int
            Atomic number, number of protons.

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.
            If `strict=True` and `atom` resolves into nuclide, not element.

        """
        identifier = self._resolve_atom_to_key(atom, strict=strict)
        return self._el2z[self._eliso2el[identifier]]

    def to_E(self, atom: Union[int, str], strict: bool = False) -> str:
        """Get element symbol of `atom`.

        Functions :py:func:`to_E` and :py:func:`to_symbol` are aliases.

        Parameters
        ----------
        atom : Union[int, str]
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.
        strict
            Allow only element identification in `atom`, not nuclide.

        Returns
        -------
        str
            Element symbol, capitalized.

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.
            If `strict=True` and `atom` resolves into nuclide, not element.

        """
        identifier = self._resolve_atom_to_key(atom, strict=strict)
        return self._eliso2el[identifier]

    def to_element(self, atom: Union[int, str], strict: bool = False) -> str:
        """Get element name of `atom`.

        Functions :py:func:`to_element` and :py:func:`to_name` are aliases.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.
        strict
            Allow only element identification in `atom`, not nuclide.

        Returns
        -------
        str
            Element name, capitalized.

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.
            If `strict=True` and `atom` resolves into nuclide, not element.

        """
        identifier = self._resolve_atom_to_key(atom, strict=strict)
        return self._el2element[self._eliso2el[identifier]]

    to_mass_number = to_A
    to_atomic_number = to_Z
    to_symbol = to_E
    to_name = to_element

    def to_period(self, atom: Union[int, str]) -> int:
        """Get period (horizontal row in periodic table) of `atom`.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.

        Returns
        -------
        int
            Period between 1 (e.g., `He`) and 7 (e.g., `U238`).

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.

        """
        Z = self.to_Z(atom)

        if Z <= 2:
            return 1
        elif Z <= 10:
            return 2
        elif Z <= 18:
            return 3
        elif Z <= 36:
            return 4
        elif Z <= 54:
            return 5
        elif Z <= 86:
            return 6
        elif Z <= 118:
            return 7
        else:
            return 8

    def to_group(self, atom: Union[int, str]) -> Union[int, None]:
        """Get group (vertical column in periodic table) of `atom`.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.

        Returns
        -------
        int
            Group between 1 (e.g., `Li`) and 18 (e.g., `KR84`).
        None
            If one of the 30 Lanthanides (Z=57-71) or Actinides (Z=89-103).

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.

        """
        Z = self.to_Z(atom)

        # yapf: disable
        if Z in    [1, 3, 11, 19, 37, 55, 87]:
            return 1
        elif Z in     [4, 12, 20, 38, 56, 88]:
            return 2
        elif Z in            [21, 39]:
            return 3
        elif Z in            [22, 40, 72, 104]:
            return 4
        elif Z in            [23, 41, 73, 105]:
            return 5
        elif Z in            [24, 42, 74, 106]:
            return 6
        elif Z in            [25, 43, 75, 107]:
            return 7
        elif Z in            [26, 44, 76, 108]:
            return 8
        elif Z in            [27, 45, 77, 109]:
            return 9
        elif Z in            [28, 46, 78, 110]:
            return 10
        elif Z in            [29, 47, 79, 111]:
            return 11
        elif Z in            [30, 48, 80, 112]:
            return 12
        elif Z in     [5, 13, 31, 49, 81, 113]:
            return 13
        elif Z in     [6, 14, 32, 50, 82, 114]:
            return 14
        elif Z in     [7, 15, 33, 51, 83, 115]:
            return 15
        elif Z in     [8, 16, 34, 52, 84, 116]:
            return 16
        elif Z in     [9, 17, 35, 53, 85, 117]:
            return 17
        elif Z in [2, 10, 18, 36, 54, 86, 118]:
            return 18
        else:
            return None
        # yapf: enable


def run_comparison():
    """Compare the existing element information for Psi4 and Cfour (in checkup_data folder) to object. Specialized use."""

    self = PeriodicTable()

    try:
        from . import checkup_data
    except ImportError:  # pragma: no cover
        print("Info for comparison (directory checkup_data) not installed. Run from source.")

    class bcolors:
        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"

    # print(bcolors.OKBLUE + '\nChecking z2element vs. Psi4 ...' + bcolors.ENDC)
    # for zz in self._z2element:
    #    if zz > 107:
    #        break
    #    assert self._z2element[zz] == checkup_data.periodictable.z2element[
    #        zz].capitalize(), 'Element {} differs from {} for Z={}'.format(
    #            z_to_element[zz], checkup_data.periodictable.z2element[zz].capitalize(), zz)

    print(bcolors.OKBLUE + "\nChecking z2el vs. Psi4 ..." + bcolors.ENDC)
    for zz in self._z2el:
        if 0 < zz < 108:
            assert (
                self._z2el[zz] == checkup_data.periodictable.z2el[zz].capitalize()
            ), "Element {} differs from {} for Z={}".format(
                self._z2el[zz], checkup_data.periodictable.z2el[zz].capitalize(), zz
            )

    print(bcolors.OKBLUE + "\nChecking el2z vs. Psi4 ..." + bcolors.ENDC)
    for el in self._el2z:
        if self._el2z[el] > 107:
            break
        if el not in ["X", "Gh"]:
            assert self._el2z[el] == checkup_data.periodictable.el2z[el.upper()], "Element {} differs from {}".format(
                self._el2z[el], checkup_data.periodictable.el2z[el.upper()]
            )

    translate = {"UUB": "Cn", "UUT": "Nh", "UUQ": "Fl", "UUP": "Mc", "UUH": "Lv", "UUS": "Ts", "UUO": "Og"}
    translate = {v: k for k, v in translate.items()}

    tol = 1.0e-5
    print(bcolors.OKBLUE + "\nChecking ({}) el2mass vs. Psi4 ...".format(tol))
    for el in self.E:
        ptel = translate.get(el, el.upper())
        if el not in ["X", "Gh"]:
            ref = self._eliso2mass[el]
            val = checkup_data.periodictable.el2mass[ptel]
            diff = abs(float(ref) - val)
            if diff > 1.0e-2:
                print(
                    bcolors.FAIL
                    + "Element {} differs by {:12.8f}: {} (this) vs {} (psi)".format(el, diff, ref, val)
                    + bcolors.ENDC
                )
            elif diff > tol:
                print("Element {} differs by {:12.8f}: {} (this) vs {} (psi)".format(el, diff, ref, val))

    tol = 1.0e-5
    print(bcolors.OKBLUE + "\nChecking ({}) el2mass vs. Cfour ...".format(tol) + bcolors.ENDC)
    for el in self.E:
        zz = self._el2z[el]
        if zz > 112:
            break
        if el not in ["X", "Gh"]:
            ref = self._eliso2mass[el]
            val = checkup_data.cfour_primary_masses[zz - 1]
            diff = abs(float(ref) - val)
            if diff > 1.0e-2:
                print(
                    bcolors.FAIL
                    + "Element {} differs by {:12.8f}: {} (this) vs {} (cfour)".format(el, diff, ref, val)
                    + bcolors.ENDC
                )
            elif diff > tol:
                print("Element {} differs by {:12.8f}: {} (this) vs {} (cfour)".format(el, diff, ref, val))

    tol = 1.0e-3
    print(bcolors.OKBLUE + "\nChecking ({}) eliso2mass vs. Psi4 ...".format(tol) + bcolors.ENDC)
    for el in self._eliso2mass:
        ptel = translate.get(el, el.upper())
        if el not in ["X", "Gh"]:
            if ptel not in checkup_data.periodictable.eliso2mass:
                print("Element {:6} missing from Psi4".format(el))
                continue
            ref = self._eliso2mass[el]
            val = checkup_data.periodictable.eliso2mass[ptel]
            diff = abs(float(ref) - val)
            if diff > 1.0e-2:
                print(
                    bcolors.FAIL
                    + "Element {:6} differs by {:12.8f}: {} (this) vs {} (psi)".format(el, diff, ref, val)
                    + bcolors.ENDC
                )
            elif diff > tol:
                print("Element {:6} differs by {:12.8f}: {} (this) vs {} (psi)".format(el, diff, ref, val))


def write_c_header(filename: str = "masses.h") -> None:
    """Write C header file defining arrays of mass and element information.

    Parameters
    ----------
    filename : str, optional
        The filename to write to.
    """
    self = PeriodicTable()

    text = [
        "#ifndef _qcelemental_masses_h_",
        "#define _qcelemental_masses_h_",
        "",
        "/* This file is autogenerated from the QCElemental python module */",
        "",
        "static const char *atomic_labels[]={",
        '"' + '","'.join(e.upper() for e in self.E) + '"',
        "};",
        "",
        "static const double an2masses[]={",
        ",".join(str(self._eliso2mass[e]) for e in self.E),
        "};",
        "",
        "static const char *mass_labels[]={",
        '"' + '","'.join(e.upper() for e in self.EA if e not in ["Gh", "X", "X0"]) + '"',
        "};",
        "",
        "static const double atomic_masses[]={",
        ",".join(str(self._eliso2mass[e]) for e in self.EA if e not in ["Gh", "X", "X0"]),
        "};",
        "",
        "#endif /* header guard */",
        "",
    ]  # yapf: disable

    with open(filename, "w") as handle:
        handle.write("\n".join(text))
    print("File written ({}). Remember to add license and clang-format it.".format(filename))


# el2mass["GH"] = 0.  # note that ghost atoms in Cfour have mass 100.
# eliso2mass["GH"] = 0.  # note that ghost atoms in Cfour have mass 100.  # encompasses el2mass
# eliso2mass["X0"] = 0.  # probably needed, just checking
# el2z["GH"] = 0

# singleton
periodictable = PeriodicTable()
