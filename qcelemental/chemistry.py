import re
import collections
from decimal import Decimal

from .exceptions import NotAnElementError


class PeriodicTable(object):
    """Nuclear and mass data about chemical elements from NIST.

    Attributes
    ----------
    A : list of int
        Mass number, number of protons and neutrons.
    Z : list of int
        Atomic number, number of protons.
    E : list of str
        Element symbol from periodic table. "Fe" capitalization.
    EA : list of str
        Nuclide symbol in E + A form, e.g., "Li6".
        List `EA` encompasses `E`; that is, both "Li6" and "Li" present.
        For hydrogen, "D" and "T" also included.
    mass : list of decimal.Decimal
        Atomic mass [u].
    mass : list of :py:class:`decimal.Decimal`
        Atomic mass [u].
        For nuclides (e.g., "Li6"), the reported mass.
        For stable elements (e.g., "Li"), the mass of the most abundant isotope ("Li7").
        For unstable elements (e.g., "Pu"), the mass of the longest-lived isotope ("Pu244").
    name : list of str
        Element name from periodic table. "Iron" capitalization.

# TODO ghost

    Parameters
    ----------
    None

    """

    def __init__(self):
        self.A = [0, 0]
        self.Z = [0]
        self.E = ['Gh']
        self.EE = ['Gh', 'X']
        self.EA = ['Gh', 'X0']
        self.mass = [Decimal(0), Decimal(0)]
        self.name = ['Ghost']

        uncertain_value = re.compile(r"""(?P<value>[\d.]+)(?P<uncertainty>\([\d#]+\))?""")
        aliases = {'D': 'H2', 'T': 'H3'}

        from . import data

        # harmless patching
        newnames = {'Uut': 'Nh', 'Uup': 'Mc', 'Uus': 'Ts'}
        for delem in data.atomic_weights_and_isotopic_compositions_for_all_elements['data']:
            symbol = delem['Atomic Symbol']
            delem['Atomic Symbol'] = newnames.get(symbol, symbol)
            for diso in delem['isotopes']:
                symbol = diso['Atomic Symbol']
                diso['Atomic Symbol'] = newnames.get(symbol, symbol)

        # element loop
        for delem in data.atomic_weights_and_isotopic_compositions_for_all_elements['data']:
            mass_of_most_common_isotope = None
            mass_number_of_most_common_isotope = None
            max_isotopic_contribution = 0.0

            # isotope loop
            for diso in delem['isotopes']:
                mobj = re.match(uncertain_value, diso['Relative Atomic Mass'])

                if mobj:
                    mass = Decimal(mobj.group('value'))
                else:
                    raise ValueError('Trouble parsing mass string ({}) for element ({})'.format(
                        diso['Relative Atomic Mass'], diso['Atomic Symbol']))

                a = int(diso['Mass Number'])

                if diso['Atomic Symbol'] in aliases:
                    self.EE.append('H')
                    self.EA.append(aliases[diso['Atomic Symbol']])
                    self.A.append(a)
                    self.mass.append(mass)

                    self.EE.append('H')
                    self.EA.append(diso['Atomic Symbol'])
                    self.A.append(a)
                    self.mass.append(mass)

                else:
                    self.EE.append(diso['Atomic Symbol'])
                    self.EA.append(diso['Atomic Symbol'] + diso['Mass Number'])
                    self.A.append(a)
                    self.mass.append(mass)

                if 'Isotopic Composition' in diso:
                    mobj = re.match(uncertain_value, diso['Isotopic Composition'])

                    if mobj:
                        if float(mobj.group('value')) > max_isotopic_contribution:
                            mass_of_most_common_isotope = mass
                            mass_number_of_most_common_isotope = a
                            max_isotopic_contribution = float(mobj.group('value'))

            # Source atomic_weights_and_isotopic_compositions_for_all_elements deals with isotopic composition of
            #   stable elements. For unstable elements, need another source for the longest-lived isotope.
            if mass_of_most_common_isotope is None:
                mass_number_of_most_common_isotope = data.longest_lived_isotope_for_unstable_elements[diso[
                    'Atomic Symbol']]
                eliso = delem['Atomic Symbol'] + str(mass_number_of_most_common_isotope)
                mass_of_most_common_isotope = self.mass[self.EA.index(eliso)]

            self.EE.append(delem['Atomic Symbol'])
            self.EA.append(delem['Atomic Symbol'])
            self.mass.append(mass_of_most_common_isotope)
            self.A.append(mass_number_of_most_common_isotope)

            z = int(delem['Atomic Number'])

            self.Z.append(z)
            self.E.append(delem['Atomic Symbol'])
            self.name.append(data.element_names[z - 1].capitalize())

        self._el2z = dict(zip(self.E, self.Z))
        #self._z2element = dict(zip(self.Z, self.name))
        self._z2el = collections.OrderedDict(zip(self.Z, self.E))
        self._element2el = dict(zip(self.name, self.E))
        self._el2element = dict(zip(self.E, self.name))

        self._eliso2mass = dict(zip(self.EA, self.mass))
        self._eliso2el = dict(zip(self.EA, self.EE))
        self._eliso2a = dict(zip(self.EA, self.A))

    def _resolve_atom_to_key(self, atom):
        """Given `atom` as element name, element symbol, nuclide symbol, atomic number, or atomic number string,
        return valid `self._eliso2mass` key, regardless of case. Raises `NotAnElementError` if unidentifiable.

        """
        try:
            self._eliso2mass[atom.capitalize()]
        except (KeyError, AttributeError):
            try:
                E = self._z2el[int(atom)]
            except (KeyError, ValueError):
                try:
                    E = self._element2el[atom.capitalize()]
                except (KeyError, AttributeError):
                    raise NotAnElementError(atom)
                else:
                    return E
            else:
                return E
        else:
            return atom.capitalize()

    def to_mass(self, atom, return_decimal=False):
        """Get atomic mass of `atom`.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.
        return_decimal : bool, optional
            Whether to preserve significant figures information by returning as Decimal or to convert to float.

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
            return mass
        else:
            return float(mass)

    def to_A(self, atom):
        """Get mass number of `atom`.

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

    def to_Z(self, atom):
        """Get atomic number of `atom`.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.

        Returns
        -------
        int
            Atomic number, number of protons.

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.

        """
        identifier = self._resolve_atom_to_key(atom)
        return self._el2z[self._eliso2el[identifier]]

    def to_E(self, atom):
        """Get element symbol of `atom`.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.

        Returns
        -------
        str
            Element symbol, capitalized.

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.

        """
        identifier = self._resolve_atom_to_key(atom)
        return self._eliso2el[identifier]

    def to_element(self, atom):
        """Get element name of `atom`.

        Parameters
        ----------
        atom : int or str
            Identifier for element or nuclide, e.g., `H`, `D`, `H2`, `He`, `hE4`.

        Returns
        -------
        str
            Element name, capitalized.

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide.

        """
        identifier = self._resolve_atom_to_key(atom)
        return self._el2element[self._eliso2el[identifier]]

    def run_comparison(self):
        """Compare the existing element information for Psi4 and Cfour (in checkup_data folder) to `self`. Specialized use."""

        from . import checkup_data

        class bcolors:
            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            WARNING = '\033[93m'
            FAIL = '\033[91m'
            ENDC = '\033[0m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'

        #print(bcolors.OKBLUE + '\nChecking z2element vs. Psi4 ...' + bcolors.ENDC)
        #for zz in self._z2element:
        #    if zz > 107:
        #        break
        #    assert self._z2element[zz] == checkup_data.periodictable.z2element[
        #        zz].capitalize(), 'Element {} differs from {} for Z={}'.format(
        #            z_to_element[zz], checkup_data.periodictable.z2element[zz].capitalize(), zz)

        print(bcolors.OKBLUE + '\nChecking z2el vs. Psi4 ...' + bcolors.ENDC)
        for zz in self._z2el:
            if zz > 0 and zz < 108:
                assert self._z2el[zz] == checkup_data.periodictable.z2el[
                    zz].capitalize(), 'Element {} differs from {} for Z={}'.format(
                        self._z2el[zz], checkup_data.periodictable.z2el[zz].capitalize(), zz)

        print(bcolors.OKBLUE + '\nChecking el2z vs. Psi4 ...' + bcolors.ENDC)
        for el in self._el2z:
            if self._el2z[el] > 107:
                break
            if el not in ['X', 'Gh']:
                assert self._el2z[
                    el] == checkup_data.periodictable.el2z[el.upper()], 'Element {} differs from {}'.format(
                        self._el2z[el], checkup_data.periodictable.el2z[el.upper()])

        translate = {'UUB': 'Cn', 'UUT': 'Nh', 'UUQ': 'Fl', 'UUP': 'Mc', 'UUH': 'Lv', 'UUS': 'Ts', 'UUO': 'Og'}
        translate = {v: k for k, v in translate.items()}

        tol = 1.e-5
        print(bcolors.OKBLUE + '\nChecking ({}) el2mass vs. Psi4 ...'.format(tol))
        for el in self.E:
            ptel = translate.get(el, el.upper())
            if el not in ['X', 'Gh']:
                ref = self._eliso2mass[el]
                val = checkup_data.periodictable.el2mass[ptel]
                diff = abs(float(ref) - val)
                if diff > 1.e-2:
                    print(bcolors.FAIL +
                          'Element {} differs by {:12.8f}: {} (this) vs {} (psi)'.format(el, diff, ref, val) +
                          bcolors.ENDC)
                elif diff > tol:
                    print('Element {} differs by {:12.8f}: {} (this) vs {} (psi)'.format(el, diff, ref, val))

        tol = 1.e-5
        print(bcolors.OKBLUE + '\nChecking ({}) el2mass vs. Cfour ...'.format(tol) + bcolors.ENDC)
        for el in self.E:
            zz = self._el2z[el]
            if zz > 112:
                break
            if el not in ['X', 'Gh']:
                ref = self._eliso2mass[el]
                val = checkup_data.cfour_primary_masses[zz - 1]
                diff = abs(float(ref) - val)
                if diff > 1.e-2:
                    print(bcolors.FAIL +
                          'Element {} differs by {:12.8f}: {} (this) vs {} (cfour)'.format(el, diff, ref, val) +
                          bcolors.ENDC)
                elif diff > tol:
                    print('Element {} differs by {:12.8f}: {} (this) vs {} (cfour)'.format(el, diff, ref, val))

        tol = 1.e-3
        print(bcolors.OKBLUE + '\nChecking ({}) eliso2mass vs. Psi4 ...'.format(tol) + bcolors.ENDC)
        for el in self._eliso2mass:
            ptel = translate.get(el, el.upper())
            if el not in ['X', 'Gh']:
                if ptel not in checkup_data.periodictable.eliso2mass:
                    print('Element {:6} missing from Psi4'.format(el))
                    continue
                ref = self._eliso2mass[el]
                val = checkup_data.periodictable.eliso2mass[ptel]
                diff = abs(float(ref) - val)
                if diff > 1.e-2:
                    print(bcolors.FAIL +
                          'Element {:6} differs by {:12.8f}: {} (this) vs {} (psi)'.format(el, diff, ref, val) +
                          bcolors.ENDC)
                elif diff > tol:
                    print('Element {:6} differs by {:12.8f}: {} (this) vs {} (psi)'.format(el, diff, ref, val))

    def write_psi4_header(self, filename='masses.h'):
        """Write C header file ``/psi4/include/psi4/masses.h`` as Psi4 wants. Specialized use."""

        text = []
        text.append('#ifndef _psi_include_masses_h_')
        text.append('#define _psi_include_masses_h_')
        text.append('')

        text.append('static const char *atomic_labels[]={')
        text.append('"' + '","'.join(e.upper() for e in self.E) + '"')
        text.append('};')
        text.append('')

        text.append('static const double an2masses[]={')
        text.append(','.join(str(self._eliso2mass[e]) for e in self.E))
        text.append('};')
        text.append('')

        text.append('static const char *mass_labels[]={')
        text.append('"' + '","'.join(e.upper() for e in self.EA if e not in ['Gh', 'X', 'X0']) + '"')
        text.append('};')
        text.append('')

        text.append('static const double atomic_masses[]={')
        text.append(','.join(str(self._eliso2mass[e]) for e in self.EA if e not in ['Gh', 'X', 'X0']))
        text.append('};')
        text.append('')

        text.append('#endif /* header guard */')
        text.append('')

        with open(filename, 'w') as handle:
            handle.write('\n'.join(text))
        print('File written ({}). Remember to add license and clang-format it.'.format(filename))


# H4, B6, Si44, Kr

#el2mass["GH"] = 0.  # note that ghost atoms in Cfour have mass 100.
#eliso2mass["GH"] = 0.  # note that ghost atoms in Cfour have mass 100.  # encompasses el2mass
#eliso2mass["X0"] = 0.  # probably needed, just checking
#el2z["GH"] = 0

# effectively, a singleton
periodictable = PeriodicTable()
