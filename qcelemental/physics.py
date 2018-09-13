"""
Contains relevant physical constants
"""

import collections
from decimal import Decimal

from . import datum


class PhysicalConstants(object):
    """CODATA 2014 physical constants set from NIST.

    Attributes
    ----------
    pc : dict of Datum
        Each physical constant is an entry in `pc`, where key is the
        lowercased string of the NIST name (or any alias) and the
        value is a Datum object with `lbl` the exact NIST name string,
        `units`, `data` value as Decimal object, and any uncertainty
        in the `comment` field.

    Parameters
    ----------
    None

    """

    _transtable = str.maketrans(' -/{', '__p_', '.,()}')

    def __init__(self):
        self.pc = collections.OrderedDict()

        from . import data

        doi = data.nist_codata_2014_metadata['distribution'][-1]['accessURL'].strip('https://dx.doi.org/')

        # physical constant loop
        # * yes, there's an extra space at the end of the Quantity key
        for pc in data.nist_codata_2014['constant']:
            value = pc['Value'].replace(' ', '')
            uncertainty = pc['Uncertainty']
            if uncertainty == '(exact)':
                value = value.replace('...', '')

            self.pc[pc['Quantity '].lower()] = datum.Datum(
                pc['Quantity '], pc['Unit'], Decimal(value), 'uncertainty={}'.format(uncertainty), doi=doi)

        self.pc['calorie-joule relationship'] = datum.Datum('calorie-joule relationship', 'J', Decimal('4.184'),
                                                            'uncertainty=(exact)')

        aliases = [
            ('h',                    'J',              self.pc['hertz-joule relationship'].data,                             'The Planck constant (Js)'),
            ('c',                    'Hz',             self.pc['inverse meter-hertz relationship'].data,                     'Speed of light (ms$^{-1}$)'),
            ('kb',                   'J',              self.pc['kelvin-joule relationship'].data,                            'The Boltzmann constant (JK$^{-1}$)'),
            ('R',                    'J mol^-1 K^-1',  self.pc['molar gas constant'].data,                                   'Universal gas constant (JK$^{-1}$mol$^{-1}$)'),
            ('bohr2angstroms',       'AA',             self.pc['bohr radius'].data * Decimal('1.E10'),                       'Bohr to Angstroms conversion factor'),
            ('bohr2m',               'm',              self.pc['bohr radius'].data,                                          'Bohr to meters conversion factor'),
            ('bohr2cm',              'cm',             self.pc['bohr radius'].data * Decimal('100'),                         'Bohr to centimeters conversion factor'),
            ('amu2g',                'g',              self.pc['atomic mass constant'].data * Decimal('1000'),               'Atomic mass units to grams conversion factor'),
            ('amu2kg',               'kg',             self.pc['atomic mass constant'].data,                                 'Atomic mass units to kg conversion factor' ),
            ('au2amu',               'u',              self.pc['electron mass in u'].data,                                   'Atomic units (m$@@e$) to atomic mass units conversion factor'),
            ('hartree2J',            'J',              self.pc['hartree energy'].data,                                       'Hartree to joule conversion factor'),
            ('hartree2aJ',           'aJ',             self.pc['hartree energy'].data * Decimal('1.E18'),                    'Hartree to attojoule (10$^{-18}$J) conversion factor'),
            ('cal2J',                'J',              self.pc['calorie-joule relationship'].data,                           'Calorie to joule conversion factor'),
            ('dipmom_au2si',         'C m',            self.pc['atomic unit of electric dipole mom.'].data,                  'Atomic units to SI units (Cm) conversion factor for dipoles'),
            ('dipmom_au2debye',      '???',            self.pc['atomic unit of electric dipole mom.'].data * Decimal('1.E21') / self.pc['hertz-inverse meter relationship'].data,
                                                                                                                             'Atomic units to Debye conversion factor for dipoles'),
            ('dipmom_debye2si',      '???',            self.pc['hertz-inverse meter relationship'].data * Decimal('1.E-21'), 'Debye to SI units (Cm) conversion factor for dipoles'),
            ('c_au',                 '',               self.pc['inverse fine-structure constant'].data,                      'Speed of light in atomic units'),
            ('hartree2ev',           'eV',             self.pc['hartree energy in ev'].data,                                 'Hartree to eV conversion factor'),
            ('hartree2wavenumbers',  'cm^-1',          self.pc['hartree-inverse meter relationship'].data * Decimal('0.01'), 'Hartree to cm$^{-1}$ conversion factor'),
            ('hartree2kcalmol',      'kcal mol^-1',    self.pc['hartree energy'].data * self.pc['avogadro constant'].data * Decimal('0.001') / self.pc['calorie-joule relationship'].data,
                                                                                                                             'Hartree to kcal mol$^{-1}$ conversion factor'),
            ('hartree2kJmol',        'kJ mol^-1',      self.pc['hartree energy'].data * self.pc['avogadro constant'].data * Decimal('0.001'), 'Hartree to kilojoule mol$^{-1}$ conversion factor'),
            ('hartree2MHz',          'MHz',            self.pc['hartree-hertz relationship'].data * Decimal('1.E-6'),        'Hartree to MHz conversion factor'),
            ('kcalmol2wavenumbers',  'kcal cm mol^-1', Decimal('10') * self.pc['calorie-joule relationship'].data / self.pc['molar planck constant times c'].data,
                                                                                                                             'kcal mol$^{-1}$ to cm$^{-1}$ conversion factor'),
            ('e0',                   'F m^-1',         self.pc['electric constant'].data,                                    'Vacuum permittivity (Fm$^{-1}$)'),
            ('na',                   'mol^-1',         self.pc['avogadro constant'].data,                                    "Avogadro's number"),
            ('me',                   'kg',             self.pc['electron mass'].data,                                        'Electron rest mass (in kg)'),
        ]  # yapf: disable

        # add alternate names for constants or derived values to help QC programs
        for alias in aliases:
            ident, units, value, comment = alias
            self.pc[ident.lower()] = datum.Datum(ident, units, value, comment)

        # add constants as directly callable member data
        for qca in self.pc.values():
            callname = qca.lbl.translate(self._transtable)
            setattr(self, callname, float(qca.data))

    def get(self, pc, return_tuple=False):
        """Access a physical constant, `pc`.

        Parameters
        ----------
        pc : str
            Case-insensitive string of physical constant with NIST name.
        return_tuple : bool, optional
            See below.

        Returns
        -------
        float
            When ``return_tuple=False``, value of physical constant.
        qcelemental.Datum
            When ``return_tuple=True``, Datum namedtuple with units, description, uncertainty, and value of physical constant as Decimal.

        """
        qca = self.pc[pc.lower()]

        if return_tuple:
            return qca
        else:
            return float(qca.data)

#       h                         'hertz-joule relationship'                  = 6.62606896E-34       # The Planck constant (Js)
#       c                         'inverse meter-hertz relationship'          = 2.99792458E8         # Speed of light (ms$^{-1}$)
#       kb                        'kelvin-joule relationship'                 = 1.3806504E-23        # The Boltzmann constant (JK$^{-1}$)
#       R                         'molar gas constant'                        = 8.314472             # Universal gas constant (JK$^{-1}$mol$^{-1}$)
#       bohr2angstroms            'Bohr radius' * 1.E10                       = 0.52917720859        # Bohr to Angstroms conversion factor
#       bohr2m                    'Bohr radius'                               = 0.52917720859E-10    # Bohr to meters conversion factor
#       bohr2cm                   'Bohr radius' * 100                         = 0.52917720859E-8     # Bohr to centimeters conversion factor
#       amu2g                     'atomic mass constant' * 1000               = 1.660538782E-24      # Atomic mass units to grams conversion factor
#       amu2kg                    'atomic mass constant'                      = 1.660538782E-27      # Atomic mass units to kg conversion factor
#       au2amu                    'electron mass in u'                        = 5.485799097E-4       # Atomic units (m$@@e$) to atomic mass units conversion factor
#       hartree2J                 'Hartree energy'                            = 4.359744E-18         # Hartree to joule conversion factor
#       hartree2aJ                'Hartree energy' * 1.E18                    = 4.359744             # Hartree to attojoule (10$^{-18}$J) conversion factor
#       cal2J                     = 4.184                # Calorie to joule conversion factor
#       dipmom_au2si              'atomic unit of electric dipole mom.'       = 8.47835281E-30       # Atomic units to SI units (Cm) conversion factor for dipoles
#       dipmom_au2debye           'atomic unit of electric dipole mom.' / ('hertz-inverse meter relationship' * 1.E-21)     = 2.54174623           # Atomic units to Debye conversion factor for dipoles
#       dipmom_debye2si           'hertz-inverse meter relationship' * 1.E-21 = 3.335640952E-30      # Debye to SI units (Cm) conversion factor for dipoles
#       c_au                      'inverse fine-structure constant'           = 137.035999679        # Speed of light in atomic units
#       hartree2ev                'Hartree energy in eV'                      = 27.21138             # Hartree to eV conversion factor
#       hartree2wavenumbers       'hartree-inverse meter relationship' * 0.01 = 219474.6             # Hartree to cm$^{-1}$ conversion factor
#       hartree2kcalmol           hartree2kJmol / cal2J                       = 627.5095             # Hartree to kcal mol$^{-1}$ conversion factor
#       hartree2kJmol             'Hartree energy'*'Avogadro constant'*0.001  = 2625.500             # Hartree to kilojoule mol$^{-1}$ conversion factor
#       hartree2MHz               'hartree-hertz relationship'                = 6.579684E9           # Hartree to MHz conversion factor
#       kcalmol2wavenumbers       10. / 'molar Planck constant times c'*4.184 = 349.7551             # kcal mol$^{-1}$ to cm$^{-1}$ conversion factor
#       e0                        'electric constant'                         = 8.854187817E-12      # Vacuum permittivity (Fm$^{-1}$)
#       na                        'Avogadro constant'                         = 6.02214179E23        # Avogadro's number
#       me                        'electron mass'                             = 9.10938215E-31       # Electron rest mass (in kg)

    def print_out(self):
        """Print name, value, and units of all physical constants."""

        print(datum.print_variables(self.pc))

    def run_comparison(self):
        """Compare the existing physical constant information for Psi4 (in checkup_data folder) to `self`. Specialized use."""

        try:
            from . import checkup_data
        except ImportError:
            print('Info for comparison (directory checkup_data) not installed. Run from source.')

        class bcolors:
            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            WARNING = '\033[93m'
            FAIL = '\033[91m'
            ENDC = '\033[0m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'

        tol = 1.e-8
        print(bcolors.OKBLUE + '\nChecking ({}) physconst vs. Psi4 ...'.format(tol) + bcolors.ENDC)
        for pc in dir(checkup_data.physconst):
            if not pc.startswith('__'):
                ref = self.get(pc)
                val = getattr(checkup_data.physconst, pc)
                rat = abs(1.0 - float(ref) / val)
                if rat > 1.e-4:
                    print(bcolors.FAIL + 'Physical Constant {} ratio differs by {:12.8f}: {} (this) vs {} (psi)'.
                          format(pc, rat, ref, val) + bcolors.ENDC)
                if rat > tol:
                    print('Physical Constant {} ratio differs by {:12.8f}: {} (this) vs {} (psi)'.format(
                        pc, rat, ref, val))

    def _get_pi(self, from_scratch=False):
        """Get pi to 36 digits (or more with mpmath)."""

        if from_scratch:
            from mpmath import mp
            mp.dps = 36
            return mp.pi
        else:
            return Decimal('3.14159265358979323846264338327950288')

    def write_psi4_header(self, filename='physconst.h'):
        """Write C header file ``/psi4/include/psi4/physconst.h`` as Psi4 wants. Specialized use."""

        pi = self._get_pi(from_scratch=False)
        tau = 2 * pi

        text = [
            '#ifndef _psi_include_physconst_h_', '#define _psi_include_physconst_h_', '', '/*',
            ' * This file is autogenerated from qcelemental python module',
            ' * Make sure that you comment any new additions to this, so they are inlined into the manual',
            ' * as well as the phyconst.py python file.  Note the format of the existing comment markers.', ' */', '',
            '// clang-format off', '#define pc_pi {}'.format(pi), '#define pc_twopi {}'.format(tau)
        ]

        for pc, qca in self.pc.items():
            callname = qca.lbl.translate(self._transtable)
            noncomment = '#define pc_{} {}'.format(callname, qca.data)
            text.append('{:80}  /*- {} [{}] {} -*/'.format(noncomment, qca.lbl, qca.units, qca.comment))
        text.append('// clang-format on')

        text.append('/* For Cray X1 compilers */')
        text.append('#ifndef M_PI')
        text.append('#define M_PI 3.14159265358979323846')
        text.append('#endif')
        text.append('')

        text.append('#endif /* header guard */')
        text.append('')

        with open(filename, 'w') as handle:
            handle.write('\n'.join(text))
        print('File written ({}). Remember to add license and clang-format it.'.format(filename))


# effectively, a singleton
constants = PhysicalConstants()
