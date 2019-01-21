"""
Molecule Object Model
"""

import os
import re
import json
import hashlib
import warnings
import collections
import numpy as np
from pydantic import BaseModel, validator
from typing import List, Tuple
from ..physical_constants import constants
from ..periodic_table import periodictable, NotAnElementError
from .common_models import Provenance
from ..util import provenance_stamp

# Rounding quantities for hashing
GEOMETRY_NOISE = 8
MASS_NOISE = 6
CHARGE_NOISE = 4


def float_prep(array, around):
    """
    Rounds floats to a common value and build positive zero's to prevent hash conflicts.
    """
    if isinstance(array, (list, np.ndarray)):
        # Round array
        array = np.around(array, around)
        # Flip zeros
        array[np.abs(array) < 5**(-(around + 1))] = 0

    elif isinstance(array, (float, int)):
        array = round(array, around)
        if array == -0.0:
            array = 0.0
    else:
        raise TypeError("Type '{}' not recognized".format(type(array).__name__))

    return array


class NPArray(np.ndarray):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            v = np.array(v)
        except:
            raise RuntimeError("Could not cast {} to NumPy Array!".format(v))
        return v


class Identifiers(BaseModel):
    """Canonical chemical identifiers"""
    molecule_hash: str = None
    molecular_formula: str = None
    smiles: str = None
    inchi: str = None
    inchikey: str = None
    canonical_explicit_hydrogen_smiles: str = None
    canonical_isomeric_explicit_hydrogen_mapped_smiles: str = None
    canonical_isomeric_explicit_hydrogen_smiles: str = None
    canonical_isomeric_smiles: str = None
    canonical_smiles: str = None

    class Config:
        allow_extra = True


# Cleanup un-initialized variables


class Molecule(BaseModel):
    id: str = None
    symbols: List[str]
    geometry: NPArray
    masses: List[float] = None
    name: str = ""
    identifiers: Identifiers = None
    comment: str = None
    molecular_charge: float = 0.0
    molecular_multiplicity: int = 1
    real: List[bool] = None
    connectivity: List[Tuple[float, float, float]] = []
    fragments: List[List[int]] = None
    fragment_charges: List[float] = None
    fragment_multiplicities: List[int] = None
    fix_com: bool = False
    fix_orientation: bool = False
    provenance: Provenance = provenance_stamp(__name__)

    class Config:
        json_encoders = {
            np.ndarray: lambda v: v.flatten().tolist(),
        }
        allow_mutation = False
        ignore_extra = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Config.allow_mutation = True  # Set this to set some immutability config
        self.symbols = [s.title() for s in self.symbols]  # Title case
        periodic_masses = [periodictable.to_mass(x) for x in self.symbols]
        if self.masses is None:  # Setup masses before fixing the orientation
            self.masses = periodic_masses
        elif np.allclose(self.masses, periodic_masses, atol=10**(-MASS_NOISE)):
            self.masses = periodic_masses
        if self.real is None:
            self.real = [True for _ in self.symbols]
        if not self.fix_orientation:
            self.geometry = float_prep(self._orient_molecule_internal(), GEOMETRY_NOISE)
        # Cleanup un-initialized variables  (more complex than Pydantic Validators allow)
        if not self.fragments:
            natoms = self.geometry.shape[0]
            self.fragments = [list(range(natoms))]
            self.fragment_charges = [self.molecular_charge]
            self.fragment_multiplicities = [self.molecular_multiplicity]
        else:
            if not self.fragment_charges:
                if np.isclose(self.molecular_charge, 0.0):
                    self.fragment_charges = [0 for _ in self.fragments]
                else:
                    raise KeyError("Fragments passed in, but not fragment charges for a charged molecule.")

            if not self.fragment_multiplicities:
                if self.molecular_multiplicity == 1:
                    self.fragment_multiplicities = [1 for _ in self.fragments]
                else:
                    raise KeyError("Fragments passed in, but not fragment multiplicities for a non-singlet molecule.")

        self.Config.allow_mutation = False  # Reset mutation

    @validator('geometry')
    def must_be_3n(cls, v, values, **kwargs):
        n = len(values['symbols'])
        try:
            v = v.reshape(n, 3)
            if v.shape != (n, 3):
                raise ValueError()
        except (ValueError, AttributeError):
            raise ValueError("Geometry must be castable to shape (N,3)!")
        return float_prep(v, GEOMETRY_NOISE)

    @validator('masses', 'real', whole=True)
    def must_be_n(cls, v, values, **kwargs):
        n = len(values['symbols'])
        if len(v) != n:
            raise ValueError("Masses and Real must be same number of entries as Symbols")
        return v

    @validator('real', whole=True)
    def populate_real(cls, v, values, **kwargs):
        # Can't use geometry here since its already been validated and not in values
        n = len(values['symbols'])
        if len(v) == 0:
            v = [True for _ in range(n)]
        return v

    @validator('fragment_charges', 'fragment_multiplicities', whole=True)
    def must_be_n_frag(cls, v, values, **kwargs):
        if 'fragments' in values:
            n = len(values['fragments'])
            if len(v) != n:
                raise ValueError("Fragment Charges and Fragment Multiplicities"
                                 " must be same number of entries as Fragments")
        else:
            raise ValueError("Cannot have Fragment Charges or Fragment Multiplicities "
                             "without Fragments")
        return v

    @validator('connectivity')
    def min_zero(cls, v):
        if v < 0:
            raise ValueError("Connectivity entries must be greater than 0")
        return v

    @property
    def hash_fields(self):
        return ["symbols", "masses", "molecular_charge", "molecular_multiplicity", "real", "geometry", "fragments",
                "fragment_charges", "fragment_multiplicities", "connectivity"]
    # ==========================
    # Non-Pydantic API functions
    # ==========================

    def orient(self):
        warnings.warn("This function is being depreciated in favor of `orient_molecule` "
                      "to match the schema. They are currently identical in function",
                      DeprecationWarning)
        return self.orient_molecule()

    def orient_molecule(self):
        """
        Centers the molecule and orients via inertia tensor before returning a new Molecule
        """
        new_dict = self.dict()
        new_dict['fix_orientation'] = False  # Instancing a new object with this set will orient
        return Molecule(**new_dict)

    def validate(self, value):
        warnings.warn("This function is now redundant since validation is handled by "
                      "class instantiation.")
        return True

    def compare(self, other, bench=None):
        """
        Checks if two molecules are identical. This is a molecular identity defined
        by scientific terms, and not programing terms, so its less rigorous than
        a programmatic equality or a memory equivalent `is`.
        """

        if isinstance(other, dict):
            other = Molecule(**other)
        elif isinstance(other, Molecule):
            pass
        else:
            raise TypeError("Comparison molecule not understood of type '{}'.".format(type(other)))

        if bench is None:
            bench = self

        match = True
        match &= bench.symbols == other.symbols
        match &= np.allclose(bench.masses, other.masses, atol=MASS_NOISE)
        match &= np.equal(bench.real, other.real).all()
        match &= np.equal(bench.fragments, other.fragments).all()
        match &= np.allclose(bench.fragment_charges, other.fragment_charges, atol=CHARGE_NOISE)
        match &= np.equal(bench.fragment_multiplicities, other.fragment_multiplicities).all()

        match &= np.allclose(bench.molecular_charge, other.molecular_charge, atol=CHARGE_NOISE)
        match &= np.equal(bench.molecular_multiplicity, other.molecular_multiplicity).all()
        match &= np.allclose(bench.geometry, other.geometry, atol=GEOMETRY_NOISE)
        return match

    def pretty_print(self):
        """Print the molecule in Angstroms. Same as :py:func:`print_out` only always in Angstroms.
        (method name in libmints is print_in_angstrom)

        """
        text = ""

        text += """    Geometry (in {0:s}), charge = {1:.1f}, multiplicity = {2:d}:\n\n""".format(
            'Angstrom', self.molecular_charge, self.molecular_multiplicity)
        text += """       Center              X                  Y                   Z       \n"""
        text += """    ------------   -----------------  -----------------  -----------------\n"""

        for i in range(len(self.geometry)):
            text += """    {0:8s}{1:4s} """.format(self.symbols[i], "" if self.real[i] else "(Gh)")
            for j in range(3):
                text += """  {0:17.12f}""".format(self.geometry[i][j] *
                                                  constants.conversion_factor("bohr", "angstroms"))
            text += "\n"
        text += "\n"

        return text

    def get_fragment(self, real, ghost=None, orient=False):
        """
        A list of real and ghost fragments:
        """

        if isinstance(real, int):
            real = [real]

        if isinstance(ghost, int):
            ghost = [ghost]
        elif ghost is None:
            ghost = []

        constructor_dict = {}

        ret_name = self.name + " (" + str(real) + "," + str(ghost) + ")"
        constructor_dict["name"] = ret_name
        # ret = Molecule(None, name=ret_name)

        if len(set(real) & set(ghost)):
            raise TypeError(
                "Molecule:get_fragment: real and ghost sets are overlapping! ({0}, {1}).".format(str(real), str(ghost)))

        geom_blocks = []
        symbols = []
        masses = []
        real_atoms = []
        fragments = []
        fragment_charges = []
        fragment_multiplicities = []

        # Loop through the real blocks
        frag_start = 0
        for frag in real:
            frag_size = len(self.fragments[frag])
            geom_blocks.append(self.geometry[self.fragments[frag]])

            for idx in self.fragments[frag]:
                symbols.append(self.symbols[idx])
                real_atoms.append(True)
                masses.append(self.masses[idx])

            fragments.append(list(range(frag_start, frag_start + frag_size)))
            frag_start += frag_size

            fragment_charges.append(float(self.fragment_charges[frag]))
            fragment_multiplicities.append(self.fragment_multiplicities[frag])

        # Set charge and multiplicity
        constructor_dict["molecular_charge"] = sum(fragment_charges)
        constructor_dict["molecular_multiplicity"] = sum(x - 1 for x in fragment_multiplicities) + 1

        # Loop through the ghost blocks
        for frag in ghost:
            frag_size = len(self.fragments[frag])
            geom_blocks.append(self.geometry[self.fragments[frag]])

            for idx in self.fragments[frag]:
                symbols.append(self.symbols[idx])
                real_atoms.append(False)
                masses.append(self.masses[idx])

            fragments.append(list(range(frag_start, frag_start + frag_size)))
            frag_start += frag_size

            fragment_charges.append(self.fragment_charges[frag])
            fragment_multiplicities.append(self.fragment_multiplicities[frag])

        constructor_dict["fragments"] = fragments
        constructor_dict["symbols"] = symbols
        constructor_dict["geometry"] = np.vstack(geom_blocks)
        constructor_dict["real"] = real_atoms
        constructor_dict["masses"] = masses

        if orient:
            constructor_dict["fix_orientation"] = False

        return Molecule(**constructor_dict)

    def to_string(self, dtype="psi4"):
        """Returns a string that can be used by a variety of programs.

        Unclear if this will be removed or renamed to "to_psi4_string" in the future
        """
        if dtype == "psi4":
            return self._to_psi4_string()
        else:
            raise KeyError("Molecule:to_string: dtype of '{}' not recognized.".format(dtype))

    def get_hash(self):
        """
        Returns the hash of the molecule.
        """

        m = hashlib.sha1()
        concat = ""

        tmp_dict = self.dict()

        np.set_printoptions(precision=16)
        for field in self.hash_fields:
            data = tmp_dict[field]
            if field == "geometry":
                tmp_dict[field] = float_prep(data, GEOMETRY_NOISE).ravel().tolist()
            elif field == "fragment_charges":
                tmp_dict[field] = float_prep(data, CHARGE_NOISE).tolist()
            elif field == "molecular_charge":
                tmp_dict[field] = float_prep(data, CHARGE_NOISE)
            elif field == "masses":
                tmp_dict[field] = float_prep(data, MASS_NOISE).tolist()

            concat += json.dumps(tmp_dict[field])  # This should only be operating on Python types now

        m.update(concat.encode("utf-8"))
        return m.hexdigest()

    def get_molecular_formula(self):
        """
        Returns the molecular formula for a molecule. Atom symbols are sorted from
        A-Z.

        Examples
        --------

        >>> methane = qcelemental.models.Molecule('''
        ... H      0.5288      0.1610      0.9359
        ... C      0.0000      0.0000      0.0000
        ... H      0.2051      0.8240     -0.6786
        ... H      0.3345     -0.9314     -0.4496
        ... H     -1.0685     -0.0537      0.1921
        ... ''')

        >>> methane.get_molecular_formula()
        CH4

        >>> hcl = qcelemental.models.Molecule('''
        ... H      0.0000      0.0000      0.0000
        ... Cl     0.0000      0.0000      1.2000
        ... ''')

        >>> hcl.get_molecular_formula()
        ClH

        """
        count = collections.Counter(x.title() for x in self.symbols)

        ret = []
        for k in sorted(count.keys()):
            c = count[k]
            ret.append(k)
            if c > 1:
                ret.append(str(c))

        return "".join(ret)

    # ============
    # Constructors
    # ============
    @classmethod
    def from_data(cls, data, dtype, orient=False, **kwargs):
        """
        Constructs a molecule object from a data structure.

        Parameters
        ----------
        data : Object
            Data to construct Molecule from. This is likely what would be loaded from a file
        dtype : {"psi4", "numpy", "json", "dict"}
            The type of data to interpret,
            no attempt to infer what type of data is done here, it must be provided
        orient: bool, optional
            Orientates the molecule to a standard frame or not.
        kwargs
            Any additional keywords to pass to the constructor

        Returns
        -------
        Molecule
            A constructed molecule class.
        """

        if dtype == "psi4":
            input_dict = cls._molecule_from_string_psi4(data)
        elif dtype == "numpy":
            input_dict = cls._molecule_from_numpy(data,
                                                  frags=kwargs.pop("frags", []),
                                                  units=kwargs.pop("units", "angstrom"))
        elif dtype == "json":
            input_dict = json.loads(data)
        elif dtype == "dict":
            input_dict = data
        else:
            raise KeyError("Dtype not understood '{}'.".format(dtype))

        input_dict["fix_orientation"] = not orient

        return cls(**input_dict)

    @classmethod
    def from_file(cls, filename, dtype=None, orient=False, **kwargs):
        """
        Constructs a molecule object from a file.

        Parameters
        ----------
        filename : str
            The filename to build
        dtype : {None, "psi4", "numpy", "json"}, optional
            The type of file to interpret.
        orient: bool, optional
            Orientates the molecule to a standard frame or not.
        kwargs
            Any additional keywords to pass to the constructor

        Returns
        -------
        Molecule
            A constructed molecule class.
        """

        ext = os.path.splitext(filename)[1]

        if dtype is None:
            if ext in [".psimol"]:
                dtype = "psi4"
            elif ext in [".npy"]:
                dtype = "numpy"
            elif ext in [".json"]:
                dtype = "json"
            else:
                raise KeyError("No dtype provided and ext '{}' not understood.".format(ext))
            print("Inferring data type to be {} from file extension".format(dtype))

        if dtype == "psi4":
            with open(filename, "r") as infile:
                data = infile.read()
        elif dtype == "numpy":
            data = np.load(filename)
        elif dtype == "json":
            with open(filename, "r") as infile:
                data = json.load(infile)
            dtype = "dict"
        else:
            raise KeyError("Dtype not understood '{}'.".format(dtype))

        return cls.from_data(data, dtype, orient=orient, **kwargs)

    # =======
    # Parsers
    # =======

    @staticmethod
    def _molecule_from_numpy(arr, frags, units="angstrom"):
        """
        Given a NumPy array of shape (N, 4) where each row is (Z_nuclear, X, Y, Z).

        Frags represents the splitting pattern for molecular fragments. Geometry must be in
        Angstroms.
        """

        arr = np.array(arr, dtype=np.double)

        if (len(arr.shape) != 2) or (arr.shape[1] != 4):
            raise AttributeError("Molecule: Molecule should be shape (N, 4) not {}.".format(arr.shape))

        if units == "bohr":
            const = 1
        elif units in ["angstrom", "angstroms"]:
            const = 1 / constants.conversion_factor("bohr", "angstroms")
        else:
            raise KeyError("Unit '{}' not understood".format(units))

        geometry = arr[:, 1:].copy() * const
        real = [True for _ in arr[:, 0]]
        symbols = [periodictable.to_E(x) for x in arr[:, 0]]

        if len(frags) and (frags[-1] != arr.shape[0]):
            frags.append(arr.shape[0])

        start = 0
        fragments = []
        fragment_charges = []
        fragment_multiplicities = []
        for fsplit in frags:
            fragments.append(list(range(start, fsplit)))
            fragment_charges.append(0.0)
            fragment_multiplicities.append(1)
            start = fsplit

        return {"geometry": geometry,
                "real": real,
                "symbols": symbols,
                "fragments": fragments,
                "fragment_charges": fragment_charges,
                "fragment_multiplicities": fragment_multiplicities
                }

    @staticmethod
    def _molecule_from_string_psi4(text):
        """Given a string *text* of psi4-style geometry specification
        (including newlines to separate lines), builds a new molecule.
        Called from constructor.

        """

        # Setup re expressions
        comment = re.compile(r'^\s*#')
        blank = re.compile(r'^\s*$')
        bohr = re.compile(r'^\s*units?[\s=]+(bohr|au|a.u.)\s*$', re.IGNORECASE)
        ang = re.compile(r'^\s*units?[\s=]+(ang|angstrom)\s*$', re.IGNORECASE)
        atom = re.compile(
            r'^(?:(?P<gh1>@)|(?P<gh2>Gh\())?(?P<label>(?P<symbol>[A-Z]{1,3})(?:(_\w+)|(\d+))?)(?(gh2)\))(?:@(?P<mass>\d+\.\d+))?$',
            re.IGNORECASE)
        cgmp = re.compile(r'^\s*(-?\d+)\s+(\d+)\s*$')
        frag = re.compile(r'^\s*--\s*$')
        # ghost = re.compile(r'@(.*)|Gh\((.*)\)', re.IGNORECASE)
        realNumber = re.compile(r"""[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?""", re.VERBOSE)

        lines = re.split('\n', text)
        glines = []
        ifrag = 0

        # Assume angstrom, we want bohr
        unit_conversion = 1 / constants.conversion_factor("bohr", "angstrom")

        output_dict = {"real": [],
                       "fragments": [],
                       "fragment_charges": [],
                       "fragment_multiplicities": []}

        for line in lines:

            # handle comments
            if comment.match(line) or blank.match(line):
                pass

            # handle units
            elif bohr.match(line):
                unit_conversion = 1.0

            elif ang.match(line):
                pass

            # Handle com
            elif line.lower().strip() in ["no_com", "nocom"]:
                output_dict["fix_com"] = True

            # handle orient
            elif line.lower().strip() in ["no_reorient", "noreorient"]:
                output_dict["fix_orientation"] = True

            # handle charge and multiplicity
            elif cgmp.match(line):
                tempCharge = int(cgmp.match(line).group(1))
                tempMultiplicity = int(cgmp.match(line).group(2))

                if ifrag == 0:
                    output_dict["molecular_charge"] = float(tempCharge)
                    output_dict["molecular_multiplicity"] = tempMultiplicity
                output_dict["fragment_charges"].append(float(tempCharge))
                output_dict["fragment_multiplicities"].append(tempMultiplicity)

            # handle fragment markers and default fragment cgmp
            elif frag.match(line):
                try:
                    output_dict["fragment_charges"][ifrag]
                except IndexError:
                    output_dict["fragment_charges"].append(0.0)
                    output_dict["fragment_multiplicities"].append(1)
                ifrag += 1
                glines.append(line)

            elif atom.match(line.split()[0].strip()):
                glines.append(line)
            else:
                raise TypeError(
                    'Molecule:create_molecule_from_string: '
                    'Unidentifiable line in geometry specification: {}'.format(line))

        # catch last default fragment cgmp
        try:
            output_dict["fragment_charges"][ifrag]
        except IndexError:
            output_dict["fragment_charges"].append(0.0)
            output_dict["fragment_multiplicities"].append(1)

        # Now go through the rest of the lines looking for fragment markers
        # There are several lines which are comment'd out as they appear to have no effect.
        # Leaving the lines in because this seems like a bug
        ifrag = 0
        iatom = 0
        tempfrag = []
        # atomSym = ""
        geometry = []
        tmpMass = []
        symbols = []
        custom_mass = False

        # handle number values

        for line in glines:

            # handle fragment markers
            if frag.match(line):
                ifrag += 1
                output_dict["fragments"].append(list(range(tempfrag[0], tempfrag[-1] + 1)))
                output_dict["real"].extend([True for _ in range(tempfrag[0], tempfrag[-1] + 1)])
                tempfrag = []

            # handle atom markers
            else:
                entries = re.split(r'\s+|\s*,\s*', line.strip())
                atomm = atom.match(line.split()[0].strip().title())
                atomSym = atomm.group('symbol')

                # We don't know whether the @C or Gh(C) notation matched. Do a quick check.
                # ghostAtom = False if (atomm.group('gh1') is None and atomm.group('gh2') is None) else True

                # Check that the atom symbol is valid
                try:
                    periodictable.to_Z(atomSym)
                except NotAnElementError:
                    raise TypeError(
                        'Molecule:create_molecule_from_string: '
                        'Illegal atom symbol in geometry specification: {}'.format(atomSym))
                symbols.append(atomSym)
                # zVal = periodictable.to_Z(atomSym)
                if atomm.group('mass') is None:
                    atomMass = periodictable.to_mass(atomSym)
                else:
                    custom_mass = True
                    atomMass = float(atomm.group('mass'))
                tmpMass.append(atomMass)

                # charge = float(zVal)
                # if ghostAtom:
                #     zVal = 0
                #     charge = 0.0

                # handle cartesians
                if len(entries) == 4:
                    tempfrag.append(iatom)
                    if realNumber.match(entries[1]):
                        xval = float(entries[1])
                    else:
                        raise TypeError("Molecule::create_molecule_from_string: "
                                        "Unidentifiable entry: {}.".format(entries[1]))

                    if realNumber.match(entries[2]):
                        yval = float(entries[2])
                    else:
                        raise TypeError("Molecule::create_molecule_from_string: "
                                        "Unidentifiable entry {}.".format(entries[2]))

                    if realNumber.match(entries[3]):
                        zval = float(entries[3])
                    else:
                        raise TypeError("Molecule::create_molecule_from_string: "
                                        "Unidentifiable entry {}.".format(entries[3]))

                    geometry.append([xval, yval, zval])
                else:
                    raise TypeError(
                        'Molecule::create_molecule_from_string: Illegal geometry specification line : {}.'
                        'You should provide either Z-Matrix or Cartesian input'.format(line))

                iatom += 1

        if custom_mass:
            output_dict["masses"] = tmpMass

        output_dict["symbols"] = symbols
        output_dict["geometry"] = np.array(geometry) * unit_conversion
        output_dict["fragments"].append(list(range(tempfrag[0], tempfrag[-1] + 1)))
        output_dict["real"].extend([True for _ in range(tempfrag[0], tempfrag[-1] + 1)])

        return output_dict

    # ===============================
    # Non-Pydantic internal functions
    # ===============================

    def _orient_molecule_internal(self):
        """
        Centers the molecule and orients via inertia tensor before returning a new set of the
        molecule geometry
        """

        new_geometry = self.geometry.copy()  # Ensure we get a copy
        # Get the mass as an array
        # Masses are needed for orientation
        np_mass = np.array(self.masses)

        # Center on Mass
        new_geometry -= np.average(new_geometry, axis=0, weights=np_mass)

        # Rotate into inertial frame
        tensor = self._inertial_tensor(new_geometry, np_mass)
        evals, evecs = np.linalg.eigh(tensor)

        new_geometry = np.dot(new_geometry, evecs)

        # Phases? Lets do the simplest thing and ensure the first atom in each column
        # that is not on a plane is positve

        phase_check = [False, False, False]

        geom_noise = 10**(-GEOMETRY_NOISE)
        for num in range(new_geometry.shape[0]):

            for x in range(3):
                if phase_check[x]:
                    continue

                val = new_geometry[num, x]

                if abs(val) < geom_noise:
                    continue

                phase_check[x] = True

                if val < 0:
                    new_geometry[:, x] *= -1

            if sum(phase_check) == 3:
                break
        return new_geometry

    def __str__(self):
        return self.pretty_print()

    @staticmethod
    def _inertial_tensor(geom, weight):
        """
        Compute the moment inertia tensor for a given geometry.
        """
        # Build inertia tensor
        tensor = np.zeros((3, 3))

        # Diagonal
        tensor[0][0] = np.sum(weight * (geom[:, 1]**2.0 + geom[:, 2]**2.0))
        tensor[1][1] = np.sum(weight * (geom[:, 0]**2.0 + geom[:, 2]**2.0))
        tensor[2][2] = np.sum(weight * (geom[:, 0]**2.0 + geom[:, 1]**2.0))

        # I(alpha, beta)
        # Off diagonal
        tensor[0][1] = -1.0 * np.sum(weight * geom[:, 0] * geom[:, 1])
        tensor[0][2] = -1.0 * np.sum(weight * geom[:, 0] * geom[:, 2])
        tensor[1][2] = -1.0 * np.sum(weight * geom[:, 1] * geom[:, 2])

        # Other half
        tensor[1][0] = tensor[0][1]
        tensor[2][0] = tensor[0][2]
        tensor[2][1] = tensor[1][2]
        return tensor

    def _to_psi4_string(self):
        """Regenerates a input file molecule specification string from the
        current state of the Molecule. Contains geometry info,
        fragmentation, charges and multiplicities, and any frame
        restriction.
        """
        text = "\n"

        # append atoms and coordinates and fragment separators with charge and multiplicity
        for num, frag in enumerate(self.fragments):
            divider = "    --"
            if num == 0:
                divider = ""

            if any(self.real[at] for at in frag):
                text += "{0:s}    \n    {1:d} {2:d}\n".format(divider, int(self.fragment_charges[num]),
                                                              self.fragment_multiplicities[num])

            for at in frag:
                if self.real[at]:
                    text += "    {0:<8s}".format(str(self.symbols[at]))
                else:
                    text += "    {0:<8s}".format("Gh(" + self.symbols[at] + ")")
                text += "    {0: 14.10f} {1: 14.10f} {2: 14.10f}\n".format(*tuple(self.geometry[at]))
        text += "\n"

        # append units and any other non-default molecule keywords
        text += "    units bohr\n"
        text += "    no_com\n"
        text += "    no_reorient\n"

        return text
