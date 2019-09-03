"""
Molecule Object Model
"""

import collections
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from pydantic import Schema, constr, validator

from ..molparse import from_arrays, from_schema, from_string, to_schema, to_string
from ..periodic_table import periodictable
from ..physical_constants import constants
from ..testing import compare, compare_values
from ..util import deserialize, measure_coordinates, provenance_stamp, which_import, msgpackext_loads
from .basemodels import ProtoModel
from .common_models import Provenance, qcschema_molecule_default
from .types import Array

# Rounding quantities for hashing
GEOMETRY_NOISE = 8
MASS_NOISE = 6
CHARGE_NOISE = 4

_extension_map = {
    ".npy": "numpy",
    ".json": "json",
    ".xyz": "xyz",
    ".psimol": "psi4",
    ".psi4": "psi4",
    ".msgpack": "msgpack",
}


def float_prep(array, around):
    """
    Rounds floats to a common value and build positive zeros to prevent hash conflicts.
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


class Identifiers(ProtoModel):
    """Canonical chemical identifiers"""

    molecule_hash: Optional[str] = None
    molecular_formula: Optional[str] = None
    smiles: Optional[str] = None
    inchi: Optional[str] = None
    inchikey: Optional[str] = None
    canonical_explicit_hydrogen_smiles: Optional[str] = None
    canonical_isomeric_explicit_hydrogen_mapped_smiles: Optional[str] = None
    canonical_isomeric_explicit_hydrogen_smiles: Optional[str] = None
    canonical_isomeric_smiles: Optional[str] = None
    canonical_smiles: Optional[str] = None

    class Config(ProtoModel.Config):
        serialize_skip_defaults = True


class Molecule(ProtoModel):
    """
    A QCSchema representation of a Molecule. This model contains
    data for symbols, geometry, connectivity, charges, fragmentation, etc while also supporting a wide array of I/O and manipulation capabilities.

    Molecule objects geometry, masses, and charges are truncated to 8, 6, and 4 decimal places respectively to assist with duplicate detection.
    """

    schema_name: constr(strip_whitespace=True, regex=qcschema_molecule_default) = Schema(  # type: ignore
        qcschema_molecule_default,
        description=(f"The QCSchema specification this model conforms to. Explicitly fixed as "
                     f"{qcschema_molecule_default}."))
    schema_version: int = Schema(  # type: ignore
        2, description="The version number of ``schema_name`` that this Molecule model conforms to.")
    validated: bool = Schema(  # type: ignore
        False,
        description="A boolean indicator (for speed purposes) that the input Molecule data has been previously checked "
        "for schema (data layout and type) and physics (e.g., non-overlapping atoms, feasible "
        "multiplicity) compliance. This should be False in most cases. A ``True`` setting "
        "should only ever be set by the constructor for this class itself or other trusted sources such as "
        "a Fractal Server or previously serialized Molecules.")

    # Required data
    symbols: Array[str] = Schema(  # type: ignore
        ...,
        description="An ordered (nat,) array-like object of atomic elemental symbols of shape (nat,). The index of "
        "this attribute sets atomic order for all other per-atom setting like ``real`` and the first "
        "dimension of ``geometry``. Ghost/Virtual atoms must have an entry in this array-like and are "
        "indicated by the matching the 0-indexed indices in ``real`` field.")
    geometry: Array[float] = Schema(  # type: ignore
        ...,
        description="An ordered (nat,3) array-like for XYZ atomic coordinates [a0]. "
        "Atom ordering is fixed; that is, a consumer who shuffles atoms must not reattach the input "
        "(pre-shuffling) molecule schema instance to any output (post-shuffling) per-atom results "
        "(e.g., gradient). Index of the first dimension matches the 0-indexed indices of all other "
        "per-atom settings like ``symbols`` and ``real``."
        "\n"
        "Can also accept array-likes which can be mapped to (nat,3) such as a 1-D list of length 3*nat, "
        "or the serialized version of the array in (3*nat,) shape; all forms will be reshaped to "
        "(nat,3) for this attribute.")

    # Molecule data
    name: Optional[str] = Schema(  # type: ignore
        None,
        description="A common or human-readable name to assign to this molecule. Can be arbitrary.")
    identifiers: Optional[Identifiers] = Schema(  # type: ignore
        None,
        description="An optional dictionary of additional identifiers by which this Molecule can be referenced, "
        "such as INCHI, canonical SMILES, etc. See the :class:``Identifiers`` model for more details.")
    comment: Optional[str] = Schema(  # type: ignore
        None,
        description="Additional comments for this Molecule. Intended for pure human/user consumption "
        "and clarity.")
    molecular_charge: float = Schema(0.0, description="The net electrostatic charge of this Molecule.")  # type: ignore
    molecular_multiplicity: int = Schema(1, description="The total multiplicity of this Molecule.")  # type: ignore

    # Atom data
    masses: Optional[Array[float]] = Schema(  # type: ignore
        None,
        description="An ordered 1-D array-like object of atomic masses [u] of shape (nat,). Index order "
        "matches the 0-indexed indices of all other per-atom settings like ``symbols`` and ``real``. If "
        "this is not provided, the mass of each atom is inferred from their most common isotope. If this "
        "is provided, it must be the same length as ``symbols`` but can accept ``None`` entries for "
        "standard masses to infer from the same index in the ``symbols`` field.")
    real: Optional[Array[bool]] = Schema(  # type: ignore
        None,
        description="An ordered 1-D array-like object of shape (nat,) indicating if each atom is real (``True``) or "
        "ghost/virtual (``False``). Index "
        "matches the 0-indexed indices of all other per-atom settings like ``symbols`` and the first "
        "dimension of ``geometry``. If this is not provided, all atoms are assumed to be real (``True``)."
        "If this is provided, the reality or ghostality of every atom must be specified.")
    atom_labels: Optional[Array[str]] = Schema(  # type: ignore
        None,
        description="Additional per-atom labels as a 1-D array-like of of strings of shape (nat,). Typical use is in "
        "model conversions, such as Elemental <-> Molpro and not typically something which should be user "
        "assigned. See the ``comments`` field for general human-consumable text to affix to the Molecule.")
    atomic_numbers: Optional[Array[np.int16]] = Schema(  # type: ignore
        None,
        description="An optional ordered 1-D array-like object of atomic numbers of shape (nat,). Index "
        "matches the 0-indexed indices of all other per-atom settings like ``symbols`` and ``real``. "
        "Values are inferred from the ``symbols`` list if not explicitly set.")
    mass_numbers: Optional[Array[np.int16]] = Schema(  # type: ignore
        None,
        description="An optional ordered 1-D array-like object of atomic *mass* numbers of shape (nat). Index "
        "matches the 0-indexed indices of all other per-atom settings like ``symbols`` and ``real``. "
        "Values are inferred from the most common isotopes of the ``symbols`` list if not explicitly set.")

    # Fragment and connection data
    connectivity: Optional[List[Tuple[int, int, float]]] = Schema(  # type: ignore
        None,
        description="The connectivity information between each atom in the ``symbols`` array. Each entry in this "
        "list is a Tuple of ``(atom_index_A, atom_index_B, bond_order)`` where the ``atom_index`` "
        "matches the 0-indexed indices of all other per-atom settings like ``symbols`` and ``real``.")
    fragments: Optional[List[Array[np.int32]]] = Schema(  # type: ignore
        None,
        description="An indication of which sets of atoms are fragments within the Molecule. This is a list of shape "
        "(nfr) of 1-D array-like objects of arbitrary length. Each entry in the list indicates a new "
        "fragment. The index "
        "of the list matches the 0-indexed indices of ``fragment_charges`` and "
        "``fragment_multiplicities``. The 1-D array-like objects are sets of atom indices indicating the "
        "atoms which compose the fragment. The atom indices match the 0-indexed indices of all other "
        "per-atom settings like ``symbols`` and ``real``.")
    fragment_charges: Optional[List[float]] = Schema(  # type: ignore
        None,
        description="The total charge of each fragment in the ``fragments`` list of shape (nfr,). The index of this "
        "list matches the 0-index indices of ``fragment`` list. Will be filled in based on a set of rules "
        "if not provided (and ``fragments`` are specified).")
    fragment_multiplicities: Optional[List[int]] = Schema(  # type: ignore
        None,
        description="The multiplicity of each fragment in the ``fragments`` list of shape (nfr,). The index of this "
        "list matches the 0-index indices of ``fragment`` list. Will be filled in based on a set of "
        "rules if not provided (and ``fragments`` are specified).")

    # Orientation
    fix_com: bool = Schema(  # type: ignore
        False,
        description="An indicator which prevents pre-processing the Molecule object to translate the Center-of-Mass "
        "to (0,0,0) in euclidean coordinate space. Will result in a different ``geometry`` than the "
        "one provided if False.")
    fix_orientation: bool = Schema(  # type: ignore
        False,
        description="An indicator which prevents pre-processes the Molecule object to orient via the inertia tensor."
        "Will result in a different ``geometry`` than the one provided if False.")
    fix_symmetry: Optional[str] = Schema(  # type: ignore
        None,
        description="Maximal point group symmetry which ``geometry`` should be treated. Lowercase.")
    # Extra
    provenance: Provenance = Schema(  # type: ignore
        provenance_stamp(__name__),
        description="The provenance information about how this Molecule (and its attributes) were generated, "
        "provided, and manipulated.")
    id: Optional[Any] = Schema(  # type: ignore
        None,
        description="A unique identifier for this Molecule object. This field exists primarily for Databases "
        "(e.g. Fractal's Server) to track and lookup this specific object and should virtually "
        "never need to be manually set.")
    extras: Dict[str, Any] = Schema(  # type: ignore
        None, description="Extra information to associate with this Molecule.")

    class Config(ProtoModel.Config):
        serialize_skip_defaults = True

    def __init__(self, orient: bool = False, validate: Optional[bool] = None, **kwargs: Any) -> None:
        """Initializes the molecule object from dictionary-like values.

        Parameters
        ----------
        orient : bool, optional
            If True, orientates the Molecule to a common reference frame.
        validate : Optional[bool], optional
            If ``None`` validation is always applied unless the ``validated`` flag is set. Otherwise uses the boolean to decide to validate the Molecule or not.
        **kwargs : Any
            The values of the Molecule object attributes.
        """
        if validate is None:
            validate = not kwargs.get("validated", False)

        if validate:
            kwargs["schema_name"] = kwargs.pop("schema_name", "qcschema_molecule")
            kwargs["schema_version"] = kwargs.pop("schema_version", 2)
            # original_keys = set(kwargs.keys())  # revive when ready to revisit sparsity

            schema = to_schema(from_schema(kwargs), dtype=kwargs["schema_version"], copy=False, np_out=True)

            kwargs["validated"] = True
            kwargs = {**kwargs, **schema}  # Allow any extra fields
            validate = True

        super().__init__(**kwargs)

        # We are pulling out the values *explicitly* so that the pydantic skip_defaults works as expected
        # All attributes set bellow are equivalent to the default set.
        values = self.__dict__

        natoms = values["geometry"].shape[0]
        if validate:
            values["symbols"] = np.core.defchararray.title(self.symbols)  # Title case for consistency

        if values["masses"] is None:  # Setup masses before fixing the orientation
            values["masses"] = np.array([periodictable.to_mass(x) for x in values["symbols"]])

        if values["real"] is None:
            values["real"] = np.ones(natoms, dtype=bool)

        if orient:
            values["geometry"] = float_prep(self._orient_molecule_internal(), GEOMETRY_NOISE)
        elif validate:
            values["geometry"] = float_prep(values["geometry"], GEOMETRY_NOISE)

        # Cleanup un-initialized variables  (more complex than Pydantic Validators allow)
        if values["fragments"] is None:
            values["fragments"] = [np.arange(natoms, dtype=np.int32)]
            values["fragment_charges"] = [values["molecular_charge"]]
            values["fragment_multiplicities"] = [values["molecular_multiplicity"]]
        else:
            if values["fragment_charges"] is None:
                if np.isclose(values["molecular_charge"], 0.0):
                    values["fragment_charges"] = [0 for _ in values["fragments"]]
                else:
                    raise KeyError("Fragments passed in, but not fragment charges for a charged molecule.")

            if values["fragment_multiplicities"] is None:
                if values["molecular_multiplicity"] == 1:
                    values["fragment_multiplicities"] = [1 for _ in values["fragments"]]
                else:
                    raise KeyError("Fragments passed in, but not fragment multiplicities for a non-singlet molecule.")

    @validator('geometry')
    def _must_be_3n(cls, v, values, **kwargs):
        n = len(values['symbols'])
        try:
            v = v.reshape(n, 3)
        except (ValueError, AttributeError):
            raise ValueError("Geometry must be castable to shape (N,3)!")
        return v

    @validator('masses', 'real', whole=True)
    def _must_be_n(cls, v, values, **kwargs):
        n = len(values['symbols'])
        if len(v) != n:
            raise ValueError("Masses and Real must be same number of entries as Symbols")
        return v

    @validator('real', whole=True)
    def _populate_real(cls, v, values, **kwargs):
        # Can't use geometry here since its already been validated and not in values
        n = len(values['symbols'])
        if len(v) == 0:
            v = np.array([True for _ in range(n)])
        return v

    @validator('fragment_charges', 'fragment_multiplicities', whole=True)
    def _must_be_n_frag(cls, v, values, **kwargs):
        if 'fragments' in values:
            n = len(values['fragments'])
            if len(v) != n:
                raise ValueError("Fragment Charges and Fragment Multiplicities"
                                 " must be same number of entries as Fragments")
        else:
            raise ValueError("Cannot have Fragment Charges or Fragment Multiplicities " "without Fragments")
        return v

    @validator('connectivity')
    def _min_zero(cls, v):
        if v < 0:
            raise ValueError("Connectivity entries must be greater than 0")
        return v

    @property
    def hash_fields(self):
        return [
            "symbols", "masses", "molecular_charge", "molecular_multiplicity", "real", "geometry", "fragments",
            "fragment_charges", "fragment_multiplicities", "connectivity"
        ]

### Non-Pydantic API functions

    def show(self, *, style: Union[str, Dict[str, Any]] = "ball_and_stick",
             canvas: Tuple[int, int] = (400, 400)) -> 'py3Dmol.view':  # type: ignore
        """Creates a 3D representation of a moleucle that can be manipulated in Jupyter Notebooks and exported as
        images (`.png`).

        Parameters
        ----------
        style : Union[str, Dict[str, Any]], optional
            Either 'ball_and_stick' or 'stick' style representations or a valid py3Dmol style dictionary.
        canvas : Tuple[int, int], optional
            The (width, height) of the display canvas in pixels

        Returns
        -------
        py3Dmol.view
            A py3dMol view object of the molecule

        """
        if not which_import("py3Dmol", return_bool=True):
            raise ModuleNotFoundError(
                f"Python module py3DMol not found. Solve by installing it: `conda install -c conda-forge py3dmol`"
            )  # pragma: no cover

        import py3Dmol  # type: ignore

        if isinstance(style, dict):
            pass
        elif style == 'ball_and_stick':
            style = {'stick': {'radius': 0.2}, 'sphere': {'scale': 0.3}}
        elif style == 'stick':
            style = {'stick': {}}
        else:
            raise KeyError(f"Style '{style}' not recognized.")

        xyzview = py3Dmol.view(width=canvas[0], height=canvas[1])

        xyzview.addModel(self.to_string("xyz", units="angstrom"), 'xyz')
        xyzview.setStyle(style)
        xyzview.zoomTo()
        return xyzview

    def measure(self, measurements: Union[List[int], List[List[int]]], *,
                degrees: bool = True) -> Union[float, List[float]]:
        """
        Takes a measurement of the moleucle from the indicies provided.

        Parameters
        ----------
        measurements : Union[List[int], List[List[int]]]
            Either a single list of indices or multiple. Return a distance, angle, or dihedral depending if
            2, 3, or 4 indices is provided, respectively. Values are returned in Bohr (distance) or degree.
        degrees : bool, optional
            Returns degrees by default, radians otherwise.

        Returns
        -------
        Union[float, List[float]]
            Either a value or list of the measured values.
        """

        return measure_coordinates(self.geometry, measurements, degrees=degrees)

    def orient_molecule(self):
        """
        Centers the molecule and orients via inertia tensor before returning a new Molecule
        """
        return Molecule(orient=True, **self.dict())

    def compare(self, other):
        """
        Checks if two molecules are identical. This is a molecular identity defined
        by scientific terms, and not programing terms, so it's less rigorous than
        a programmatic equality or a memory equivalent `is`.
        """

        if isinstance(other, dict):
            other = Molecule(orient=False, **other)
        elif isinstance(other, Molecule):
            pass
        else:
            raise TypeError("Comparison molecule not understood of type '{}'.".format(type(other)))

        match = True
        match &= np.array_equal(self.symbols, other.symbols)
        match &= np.allclose(self.masses, other.masses, atol=(10**-MASS_NOISE))
        match &= np.array_equal(self.real, other.real)
        match &= np.array_equal(self.fragments, other.fragments)
        match &= np.allclose(self.fragment_charges, other.fragment_charges, atol=(10**-CHARGE_NOISE))
        match &= np.array_equal(self.fragment_multiplicities, other.fragment_multiplicities)

        match &= np.allclose(self.molecular_charge, other.molecular_charge, atol=(10**-CHARGE_NOISE))
        match &= np.array_equal(self.molecular_multiplicity, other.molecular_multiplicity)
        match &= np.allclose(self.geometry, other.geometry, atol=(10**-GEOMETRY_NOISE))
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
        # text += "\n"

        return text

    def get_fragment(self,
                     real: Union[int, List],
                     ghost: Optional[Union[int, List]] = None,
                     orient: bool = False,
                     group_fragments: bool = True) -> 'Molecule':
        """Get new Molecule with fragments preserved, dropped, or ghosted.

        Parameters
        ----------
        real
            Fragment index or list of indices (0-indexed) to be real atoms in new Molecule.
        ghost
            Fragment index or list of indices (0-indexed) to be ghost atoms (basis fns only) in new Molecule.
        orient
            Whether or not to align (inertial frame) and phase geometry upon new Molecule instantiation
            (according to _orient_molecule_internal)?
        group_fragments
            Whether or not to group real fragments at the start of the atom list and ghost fragments toward the back.
            Previous to ``v0.5``, this was always effectively True. True is handy for finding duplicate
            (atom-order-independent) molecules by hash. False preserves fragment order (though collapsing gaps for
            absent fragments) like Psi4's ``extract_subsets``. False is handy for gradients where atom order of
            returned values matters.

        Returns
        -------
        mol
            New ``py::class:qcelemental.model.Molecule`` with ``self``\'s fragments present, ghosted, or absent.

        """
        if isinstance(real, int):
            real = [real]

        if isinstance(ghost, int):
            ghost = [ghost]
        elif ghost is None:
            ghost = []

        constructor_dict: Dict = {}

        ret_name = (self.name if self.name is not None else '') + " (" + str(real) + "," + str(ghost) + ")"
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
        atom_size = 0

        if group_fragments:

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

        else:
            # List[Array[np.int32]]
            at2fr: List[Union[int, None]] = [None] * len(self.symbols)
            for ifr, fr in enumerate(self.fragments):
                for iat in fr:
                    at2fr[iat] = ifr

            at2at: List[Union[int, None]] = [None] * len(self.symbols)
            for iat in range(len(self.symbols)):
                ifr = at2fr[iat]

                if ifr in real or ifr in ghost:
                    geom_blocks.append(self.geometry[iat])
                    symbols.append(self.symbols[iat])
                    real_atoms.append(ifr in real)
                    masses.append(self.masses[iat])

                    at2at[iat] = atom_size
                    atom_size += 1

                else:
                    at2at[iat] = None

            for ifr, fr in enumerate(self.fragments):
                if ifr in real or ifr in ghost:
                    fragments.append([at2at[iat] for iat in fr])

                if ifr in real:
                    fragment_charges.append(self.fragment_charges[ifr])
                    fragment_multiplicities.append(self.fragment_multiplicities[ifr])

                elif ifr in ghost:
                    fragment_charges.append(0)
                    fragment_multiplicities.append(1)

            assert None not in fragments

        constructor_dict["fragments"] = fragments
        constructor_dict["fragment_charges"] = fragment_charges
        constructor_dict["fragment_multiplicities"] = fragment_multiplicities
        constructor_dict["symbols"] = symbols
        constructor_dict["geometry"] = np.vstack(geom_blocks)
        constructor_dict["real"] = real_atoms
        constructor_dict["masses"] = masses

        return Molecule(orient=orient, **constructor_dict)

    def to_string(  # type: ignore
            self,
            dtype: str,
            units: str = None,
            *,
            atom_format: str = None,
            ghost_format: str = None,
            width: int = 17,
            prec: int = 12,
            return_data: bool = False):
        """Returns a string that can be used by a variety of programs.

        Unclear if this will be removed or renamed to "to_psi4_string" in the future

        Suggest psi4 --> psi4frag and psi4 route to to_string
        """
        molrec = from_schema(self.dict())
        return to_string(molrec,
                         dtype=dtype,
                         units=units,
                         atom_format=atom_format,
                         ghost_format=ghost_format,
                         width=width,
                         prec=prec,
                         return_data=return_data)

    def get_hash(self):
        """
        Returns the hash of the molecule.
        """

        m = hashlib.sha1()
        concat = ""

        tmp_dict = super().dict(skip_defaults=False)

        np.set_printoptions(precision=16)
        for field in self.hash_fields:
            data = tmp_dict[field]
            if field == "geometry":
                data = float_prep(data, GEOMETRY_NOISE)
            elif field == "fragment_charges":
                data = float_prep(data, CHARGE_NOISE)
            elif field == "molecular_charge":
                data = float_prep(data, CHARGE_NOISE)
            elif field == "masses":
                data = float_prep(data, MASS_NOISE)

            concat += json.dumps(data, default=lambda x: x.ravel().tolist())

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
                  data: Union[str, Dict[str, Any], np.array, bytes],
                  dtype: Optional[str] = None,
                  *,
                  orient: bool = False,
                  validate: bool = None,
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
            elif isinstance(dtype, bytes):
                dtype = "msgpack"
            else:
                raise TypeError("Input type not understood, please supply the 'dtype' kwarg.")

        if dtype in ["string", "psi4", "psi4+", "xyz", "xyz+"]:
            molrec = from_string(data, enable_qm=True, missing_enabled_return_qm='minimal')
            assert isinstance(molrec, dict)
            input_dict = to_schema(molrec["qm"], dtype=2)
            validate = True
        elif dtype == "numpy":
            data = np.asarray(data)
            data = {
                "geom": data[:, 1:],
                "elez": data[:, 0],
                "units": kwargs.pop("units", "Angstrom"),
                "fragment_separators": kwargs.pop("frags", [])
            }
            input_dict = to_schema(from_arrays(**data), dtype=2)
            validate = True
        elif dtype == "msgpack":
            assert isinstance(data, bytes)
            input_dict = msgpackext_loads(data)
        elif dtype == "json":
            assert isinstance(data, str)
            input_dict = json.loads(data)
        elif dtype == "dict":
            assert isinstance(data, dict)
            input_dict = data
        else:
            raise KeyError("Dtype not understood '{}'.".format(dtype))

        return cls(orient=orient, validate=validate, **input_dict)

    @classmethod
    def from_file(cls, filename: str, dtype: Optional[str] = None, *, orient: bool = False, **kwargs):
        """
        Constructs a molecule object from a file.

        Parameters
        ----------
        filename : str
            The filename to build
        dtype : Optional[str], optional
            The type of file to interpret.
        orient : bool, optional
            Orientates the molecule to a standard frame or not.
        **kwargs
            Any additional keywords to pass to the constructor

        Returns
        -------
        Molecule
            A constructed molecule class.

        """

        ext = Path(filename).suffix

        if dtype is None:
            if ext in _extension_map:
                dtype = _extension_map[ext]
            else:
                # Let `from_string` try to sort it
                dtype = "string"

        # Raw string type, read and pass through
        if dtype in ["string", "xyz", "psi4"]:
            with open(filename, "r") as infile:
                data = infile.read()
        elif dtype == "numpy":
            data = np.load(filename)
        elif dtype == "json":
            with open(filename, "r") as infile:
                data = json.load(infile)
            dtype = "dict"
        elif dtype == "msgpack":
            with open(filename, "rb") as infile_bytes:
                data = deserialize(infile_bytes.read(), encoding="msgpack-ext")
            dtype = "dict"
        else:
            raise KeyError("Dtype not understood '{}'.".format(dtype))

        return cls.from_data(data, dtype, orient=orient, **kwargs)

    def to_file(self, filename: str, dtype: Optional[str] = None) -> None:
        """Writes the Molecule to a file.

        Parameters
        ----------
        filename : str
            The filename to write to
        dtype : Optional[str], optional
            The type of file to write, attempts to infer dtype from the filename if not provided.

        """
        ext = Path(filename).suffix

        if dtype is None:
            if ext in _extension_map:
                dtype = _extension_map[ext]
            else:
                raise KeyError(f"Could not infer dtype from filename: `{filename}`")

        flags = "w"
        if dtype in ["xyz", "psi4"]:
            stringified = self.to_string(dtype)
        elif dtype in ["json"]:
            stringified = self.serialize("json")
        elif dtype in ["msgpack", "msgpack-ext"]:
            stringified = self.serialize("msgpack-ext")
            flags = "wb"
        elif dtype in ["numpy"]:
            elements = np.array(self.atomic_numbers).reshape(-1, 1)
            npmol = np.hstack((elements, self.geometry * constants.conversion_factor("bohr", "angstroms")))
            np.save(filename, npmol)
            return

        else:
            raise KeyError(f"Dtype `{dtype}` is not valid")

        with open(filename, flags) as handle:
            handle.write(stringified)

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
        tensor = self._inertial_tensor(new_geometry, weight=np_mass)
        _, evecs = np.linalg.eigh(tensor)

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

    def __str__(self) -> str:
        return self.pretty_print()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}' formula='{self.get_molecular_formula()}' hash='{self.get_hash()[:7]}')>"

    def _repr_html_(self) -> str:
        try:
            return self.show()._repr_html_()
        except ModuleNotFoundError:
            return f"<p>{repr(self)[1:-1]}</p>"

    @staticmethod
    def _inertial_tensor(geom, *, weight):
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

    def nuclear_repulsion_energy(self, ifr: int = None) -> float:
        """Nuclear repulsion energy.

        Parameters
        ----------
        ifr : int, optional
            If not `None`, only compute for the `ifr`-th (0-indexed) fragment.

        Returns
        -------
        Nuclear repulsion energy in entire molecule or in fragment.

        """
        Zeff = [z * int(real) for z, real in zip(self.atomic_numbers, self.real)]
        atoms = list(range(self.geometry.shape[0]))

        if ifr is not None:
            atoms = self.fragments[ifr]

        nre = 0.
        for iat1, at1 in enumerate(atoms):
            for at2 in atoms[:iat1]:
                dist = np.linalg.norm(self.geometry[at1] - self.geometry[at2])
                nre += Zeff[at1] * Zeff[at2] / dist
        return nre

    def nelectrons(self, ifr: int = None) -> int:
        """Number of electrons.

        Parameters
        ----------
        ifr : int, optional
            If not `None`, only compute for the `ifr`-th (0-indexed) fragment.

        Returns
        -------
        Number of electrons in entire molecule or in fragment.

        """
        Zeff = [z * int(real) for z, real in zip(self.atomic_numbers, self.real)]

        if ifr is None:
            nel = sum(Zeff) - self.molecular_charge

        else:
            nel = sum([zf for iat, zf in enumerate(Zeff) if iat in self.fragments[ifr]]) - self.fragment_charges[ifr]

        return int(nel)

    def align(self,
              ref_mol,
              *,
              do_plot=False,
              verbose=0,
              atoms_map=False,
              run_resorting=False,
              mols_align=False,
              run_to_completion=False,
              uno_cutoff=1.e-3,
              run_mirror=False):
        """Finds shift, rotation, and atom reordering of `concern_mol` (self)
        that best aligns with `ref_mol`.

        Wraps :py:func:`qcel.molutil.B787` for :py:class:`qcel.models.Molecule`.
        Employs the Kabsch, Hungarian, and Uno algorithms to exhaustively locate
        the best alignment for non-oriented, non-ordered structures.

        Parameters
        ----------
        concern_mol : qcel.models.Molecule
            Molecule of concern, to be shifted, rotated, and reordered into
            best coincidence with `ref_mol`.
        ref_mol : qcel.models.Molecule
            Molecule to match.
        atoms_map : bool, optional
            Whether atom1 of `ref_mol` corresponds to atom1 of `concern_mol`, etc.
            If true, specifying `True` can save much time.
        mols_align : bool, optional
            Whether `ref_mol` and `concern_mol` have identical geometries by eye
            (barring orientation or atom mapping) and expected final RMSD = 0.
            If `True`, procedure is truncated when RMSD condition met, saving time.
        do_plot : bool, optional
            Pops up a mpl plot showing before, after, and ref geometries.
        run_to_completion : bool, optional
            Run reorderings to completion (past RMSD = 0) even if unnecessary because
            `mols_align=True`. Used to test worst-case timings.
        run_resorting : bool, optional
            Run the resorting machinery even if unnecessary because `atoms_map=True`.
        uno_cutoff : float, optional
            TODO
        run_mirror : bool, optional
            Run alternate geometries potentially allowing best match to `ref_mol`
            from mirror image of `concern_mol`. Only run if system confirmed to
            be nonsuperimposable upon mirror reflection.
        verbose : int, optional
            Print level.

        Returns
        -------
        Molecule, data
            Molecule is internal geometry of `self` optimally aligned and atom-ordered
              to `ref_mol`. Presently all fragment information is discarded.
            `data['rmsd']` is RMSD [A] between `ref_mol` and the optimally aligned
            geometry computed.
            `data['mill']` is a AlignmentMill namedtuple with fields
            (shift, rotation, atommap, mirror) that prescribe the transformation
            from `concern_mol` and the optimally aligned geometry.

        """
        from ..molutil.align import B787

        rgeom = np.array(ref_mol.geometry)
        runiq = np.asarray([
            hashlib.sha1((sym + str(mas)).encode('utf-8')).hexdigest()
            for sym, mas in zip(ref_mol.symbols, ref_mol.masses)
        ])
        concern_mol = self
        cgeom = np.array(concern_mol.geometry)
        cmass = np.array(concern_mol.masses)
        celem = np.array(concern_mol.symbols)
        celez = np.array(concern_mol.atomic_numbers)
        cuniq = np.asarray([
            hashlib.sha1((sym + str(mas)).encode('utf-8')).hexdigest()
            for sym, mas in zip(concern_mol.symbols, concern_mol.masses)
        ])

        rmsd, solution = B787(cgeom=cgeom,
                              rgeom=rgeom,
                              cuniq=cuniq,
                              runiq=runiq,
                              do_plot=do_plot,
                              verbose=verbose,
                              atoms_map=atoms_map,
                              run_resorting=run_resorting,
                              mols_align=mols_align,
                              run_to_completion=run_to_completion,
                              run_mirror=run_mirror,
                              uno_cutoff=uno_cutoff)

        ageom, amass, aelem, aelez, _ = solution.align_system(cgeom, cmass, celem, celez, cuniq, reverse=False)
        adict = from_arrays(geom=ageom,
                            mass=amass,
                            elem=aelem,
                            elez=aelez,
                            units='Bohr',
                            molecular_charge=concern_mol.molecular_charge,
                            molecular_multiplicity=concern_mol.molecular_multiplicity,
                            fix_com=True,
                            fix_orientation=True)
        amol = Molecule(validate=False, **to_schema(adict, dtype=2))

        # TODO -- can probably do more with fragments in amol now that
        #         Mol is something with non-contig frags. frags now discarded.

        assert compare_values(concern_mol.nuclear_repulsion_energy(),
                              amol.nuclear_repulsion_energy(),
                              'Q: concern_mol-->returned_mol NRE uncorrupted',
                              atol=1.e-4,
                              quiet=(verbose > 1))
        if mols_align:
            assert compare_values(ref_mol.nuclear_repulsion_energy(),
                                  amol.nuclear_repulsion_energy(),
                                  'Q: concern_mol-->returned_mol NRE matches ref_mol',
                                  atol=1.e-4,
                                  quiet=(verbose > 1))
            assert compare(True,
                           np.allclose(ref_mol.geometry, amol.geometry, atol=4),
                           'Q: concern_mol-->returned_mol geometry matches ref_mol',
                           quiet=(verbose > 1))

        return amol, {'rmsd': rmsd, 'mill': solution}

    def scramble(self,
                 *,
                 do_shift: bool = True,
                 do_rotate=True,
                 do_resort=True,
                 deflection=1.0,
                 do_mirror=False,
                 do_plot=False,
                 do_test=False,
                 run_to_completion=False,
                 run_resorting=False,
                 verbose=0):
        """Generate a Molecule with random or directed translation, rotation, and atom shuffling.
        Optionally, check that the aligner returns the opposite transformation.

        Parameters
        ----------
        ref_mol : qcel.models.Molecule
            Molecule to perturb.
        do_shift : bool or array-like, optional
            Whether to generate a random atom shift on interval [-3, 3) in each
            dimension (`True`) or leave at current origin. To shift by a specified
            vector, supply a 3-element list.
        do_rotate : bool or array-like, optional
            Whether to generate a random 3D rotation according to algorithm of Arvo.
            To rotate by a specified matrix, supply a 9-element list of lists.
        do_resort : bool or array-like, optional
            Whether to shuffle atoms (`True`) or leave 1st atom 1st, etc. (`False`).
            To specify shuffle, supply a nat-element list of indices.
        deflection : float, optional
            If `do_rotate`, how random a rotation: 0.0 is no change, 0.1 is small
            perturbation, 1.0 is completely random.
        do_mirror : bool, optional
            Whether to construct the mirror image structure by inverting y-axis.
        do_plot : bool, optional
            Pops up a mpl plot showing before, after, and ref geometries.
        do_test : bool, optional
            Additionally, run the aligner on the returned Molecule and check that
            opposite transformations obtained.
        run_to_completion : bool, optional
            By construction, scrambled systems are fully alignable (final RMSD=0).
            Even so, `True` turns off the mechanism to stop when RMSD reaches zero
            and instead proceed to worst possible time.
        run_resorting : bool, optional
            Even if atoms not shuffled, test the resorting machinery.
        verbose : int, optional
            Print level.

        Returns
        -------
        Molecule, data
            Molecule is scrambled copy of `ref_mol` (self).
            `data['rmsd']` is RMSD [A] between `ref_mol` and the scrambled geometry.
            `data['mill']` is a AlignmentMill namedtuple with fields
            (shift, rotation, atommap, mirror) that prescribe the transformation
            from `ref_mol` to the returned geometry.

        Raises
        ------
        AssertionError
            If `do_test=True` and aligner sanity check fails for any of the reverse
            transformations.

        """
        from ..molutil.align import compute_scramble

        ref_mol = self
        rgeom = np.array(ref_mol.geometry)
        rmass = np.array(ref_mol.masses)
        relem = np.array(ref_mol.symbols)
        relez = np.array(ref_mol.atomic_numbers)
        runiq = np.asarray([
            hashlib.sha1((sym + str(mas)).encode('utf-8')).hexdigest()
            for sym, mas in zip(ref_mol.symbols, ref_mol.masses)
        ])
        nat = rgeom.shape[0]

        perturbation = compute_scramble(rgeom.shape[0],
                                        do_shift=do_shift,
                                        do_rotate=do_rotate,
                                        deflection=deflection,
                                        do_resort=do_resort,
                                        do_mirror=do_mirror)
        cgeom, cmass, celem, celez, cuniq = perturbation.align_system(rgeom, rmass, relem, relez, runiq, reverse=True)
        cmolrec = from_arrays(
            geom=cgeom,
            mass=cmass,
            elem=celem,
            elez=celez,
            units='Bohr',
            molecular_charge=ref_mol.molecular_charge,
            molecular_multiplicity=ref_mol.molecular_multiplicity,
            # copying fix_* vals rather than outright True. neither way great
            fix_com=ref_mol.fix_com,
            fix_orientation=ref_mol.fix_orientation)
        cmol = Molecule(validate=False, **to_schema(cmolrec, dtype=2))

        rmsd = np.linalg.norm(cgeom - rgeom) * constants.bohr2angstroms / np.sqrt(nat)
        if verbose >= 1:
            print('Start RMSD = {:8.4f} [A]'.format(rmsd))

        if do_test:
            _, data = cmol.align(ref_mol,
                                 do_plot=do_plot,
                                 atoms_map=(not do_resort),
                                 run_resorting=run_resorting,
                                 mols_align=True,
                                 run_to_completion=run_to_completion,
                                 run_mirror=do_mirror,
                                 verbose=verbose)
            solution = data['mill']

            assert compare(True,
                           np.allclose(solution.shift, perturbation.shift, atol=6),
                           'shifts equiv',
                           quiet=(verbose > 1))
            if not do_resort:
                assert compare(True,
                               np.allclose(solution.rotation.T, perturbation.rotation),
                               'rotations transpose',
                               quiet=(verbose > 1))
            if solution.mirror:
                assert compare(True, do_mirror, 'mirror allowed', quiet=(verbose > 1))

        return cmol, {'rmsd': rmsd, 'mill': perturbation}


# auto_gen_docs_on_demand(Molecule)
