"""
Molecule Object Model
"""

import collections
import hashlib
import json
import os
from typing import Any, Dict, List, Tuple, Optional, Union

import numpy as np
from pydantic import BaseModel, validator, constr

from ..molparse import from_arrays, from_schema, from_string, to_schema
from ..periodic_table import periodictable
from ..physical_constants import constants
from ..util import measure_coordinates, provenance_stamp
from .common_models import Provenance, ndarray_encoder, qcschema_molecule_default

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


class NDArray(np.ndarray):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            v = np.array(v, dtype=np.double)
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
        allow_mutation = False
        extra = "forbid"

    def dict(self, *args, **kwargs):
        return super().dict(*args, **{**kwargs, **{"skip_defaults": True}})


class Molecule(BaseModel):

    # Required data
    schema_name: constr(strip_whitespace=True, regex=qcschema_molecule_default) = qcschema_molecule_default
    schema_version: int = 2
    symbols: List[str]
    # geometry: List[float]
    geometry: NDArray

    # Molecule data
    name: str = ""
    identifiers: Identifiers = None
    comment: str = None
    molecular_charge: float = 0.0
    molecular_multiplicity: int = 1

    # Atom data
    masses: List[float] = None
    real: List[bool] = None
    atom_labels: List[str] = None
    atomic_numbers: List[int] = None
    mass_numbers: List[int] = None

    # Fragment and connection data
    connectivity: List[Tuple[int, int, float]] = []
    fragments: List[List[int]] = None
    fragment_charges: List[float] = None
    fragment_multiplicities: List[int] = None

    # Orientation
    fix_com: bool = False
    fix_orientation: bool = False
    fix_symmetry: str = None

    # Extra
    provenance: Provenance = provenance_stamp(__name__)
    id: Optional[str] = None
    extras: Dict[str, Any] = None

    class Config:
        json_encoders = {**ndarray_encoder}
        allow_mutation = False
        extra = "forbid"

    def __init__(self, orient=False, validate=True, **kwargs):
        if validate:
            kwargs["schema_name"] = kwargs.pop("schema_name", "qcschema_molecule")
            kwargs["schema_version"] = kwargs.pop("schema_version", 2)
            # original_keys = set(kwargs.keys())  # revive when ready to revisit sparsity

            schema = to_schema(from_schema(kwargs), dtype=kwargs["schema_version"])

            kwargs = {**kwargs, **schema}  # Allow any extra fields

        super().__init__(**kwargs)

        # We are pulling out the values *explicitly* so that the pydantic skip_defaults works as expected
        # All attributes set bellow are equivalent to the default set.
        values = self.__values__

        values["symbols"] = [s.title() for s in self.symbols]  # Title case

        if values["masses"] is None:  # Setup masses before fixing the orientation
            values["masses"] = [periodictable.to_mass(x) for x in values["symbols"]]

        if values["real"] is None:
            values["real"] = [True for _ in values["symbols"]]

        if orient:
            values["geometry"] = float_prep(self._orient_molecule_internal(), GEOMETRY_NOISE)
        else:
            values["geometry"] = float_prep(values["geometry"], GEOMETRY_NOISE)

        # Cleanup un-initialized variables  (more complex than Pydantic Validators allow)
        if not values["fragments"]:
            natoms = values["geometry"].shape[0]
            values["fragments"] = [list(range(natoms))]
            values["fragment_charges"] = [values["molecular_charge"]]
            values["fragment_multiplicities"] = [values["molecular_multiplicity"]]
        else:
            if not values["fragment_charges"]:
                if np.isclose(values["molecular_charge"], 0.0):
                    values["fragment_charges"] = [0 for _ in values["fragments"]]
                else:
                    raise KeyError("Fragments passed in, but not fragment charges for a charged molecule.")

            if not values["fragment_multiplicities"]:
                if values["molecular_multiplicity"] == 1:
                    values["fragment_multiplicities"] = [1 for _ in values["fragments"]]
                else:
                    raise KeyError("Fragments passed in, but not fragment multiplicities for a non-singlet molecule.")

    @validator('geometry')
    def must_be_3n(cls, v, values, **kwargs):
        n = len(values['symbols'])
        try:
            v = v.reshape(n, 3)
        except (ValueError, AttributeError):
            raise ValueError("Geometry must be castable to shape (N,3)!")
        return v

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
            raise ValueError("Cannot have Fragment Charges or Fragment Multiplicities " "without Fragments")
        return v

    @validator('connectivity')
    def min_zero(cls, v):
        if v < 0:
            raise ValueError("Connectivity entries must be greater than 0")
        return v

    @property
    def hash_fields(self):
        return [
            "symbols", "masses", "molecular_charge", "molecular_multiplicity", "real", "geometry", "fragments",
            "fragment_charges", "fragment_multiplicities", "connectivity"
        ]

    def dict(self, *args, **kwargs):
        return super().dict(*args, **{**kwargs, **{"skip_defaults": True}})

    def json_dict(self, *args, **kwargs):
        return json.loads(self.json(*args, **kwargs))

### Non-Pydantic API functions

    def measure(self, measurements, degrees=True):
        """
        Takes a measurement of the moleucle from the indicies provided.
        """

        return measure_coordinates(self.geometry, measurements, degrees=degrees)

    def orient_molecule(self):
        """
        Centers the molecule and orients via inertia tensor before returning a new Molecule
        """
        return Molecule(orient=True, **self.dict())

    def compare(self, other, bench=None):
        """
        Checks if two molecules are identical. This is a molecular identity defined
        by scientific terms, and not programing terms, so its less rigorous than
        a programmatic equality or a memory equivalent `is`.
        """

        if isinstance(other, dict):
            other = Molecule(orient=False, **other)
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
                text += """  {0:17.12f}""".format(
                    self.geometry[i][j] * constants.conversion_factor("bohr", "angstroms"))
            text += "\n"
        # text += "\n"

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
            raise TypeError("Molecule:get_fragment: real and ghost sets are overlapping! ({0}, {1}).".format(
                str(real), str(ghost)))

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

            fragment_charges.append(0)
            fragment_multiplicities.append(1)

        constructor_dict["fragments"] = fragments
        constructor_dict["fragment_charges"] = fragment_charges
        constructor_dict["fragment_multiplicities"] = fragment_multiplicities
        constructor_dict["symbols"] = symbols
        constructor_dict["geometry"] = np.vstack(geom_blocks)
        constructor_dict["real"] = real_atoms
        constructor_dict["masses"] = masses

        return Molecule(orient=orient, **constructor_dict)

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

        tmp_dict = super().dict()

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

    ### Constructors

    @classmethod
    def from_data(cls,
                  data: Union[str, Dict[str, Any], np.array],
                  dtype: Optional[str]=None,
                  *,
                  orient: bool=False,
                  validate: bool=True,
                  **kwargs: Dict[str, Any]) -> 'Molecule':
        """
        Constructs a molecule object from a data structure.

        Parameters
        ----------
        data : Union[str, Dict[str, Any], np.array]
            Data to construct Molecule from
        dtype : Optional[str], optional
            How to interpret the data, if not passed attempts to discover this based on input type.
        orient : bool, optional
            Orientates the molecule to a standard frame or not.
        validate : bool, optional
            Validates the molecule or not.
        **kwargs : Dict[str, Any]
            Additional kwargs to pass to the constructors.

        Returns
        -------
        Molecule
            A constructed molecule class.

        """
        if dtype is None:
            if isinstance(data, str):
                dtype = "string"
            elif isinstance(data, np.ndarray):
                dtype = "numpy"
            elif isinstance(data, dict):
                dtype = "dict"
            else:
                raise TypeError("Input type not understood, please supply the 'dtype' kwarg.")

        if dtype in ["string", "psi4", "psi4+", "xyz", "xyz+"]:
            input_dict = to_schema(from_string(data)["qm"], dtype=2)
            validate = False  # Already validated, no need to do it twice
        elif dtype == "numpy":
            data = np.asarray(data)
            data = {
                "geom": data[:, 1:],
                "elez": data[:, 0],
                "units": kwargs.pop("units", "Angstrom"),
                "fragment_separators": kwargs.pop("frags", [])
            }
            input_dict = to_schema(from_arrays(**data), dtype=2)
            validate = False
        elif dtype == "json":
            input_dict = json.loads(data)
        elif dtype == "dict":
            input_dict = data
        else:
            raise KeyError("Dtype not understood '{}'.".format(dtype))

        return cls(orient=orient, validate=validate, **input_dict)

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
            # print("Inferring data type to be {} from file extension".format(dtype))

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

    ### Non-Pydantic internal functions

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
        tensor[1][0] = tensor[0][1] = -1.0 * np.sum(weight * geom[:, 0] * geom[:, 1])
        tensor[2][0] = tensor[0][2] = -1.0 * np.sum(weight * geom[:, 0] * geom[:, 2])
        tensor[2][1] = tensor[1][2] = -1.0 * np.sum(weight * geom[:, 1] * geom[:, 2])
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
                text += "{0:s}    \n    {1:d} {2:d}\n".format(divider,
                                                              int(self.fragment_charges[num]),
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
