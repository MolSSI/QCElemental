from __future__ import annotations

import math
import warnings
from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from ..exceptions import MoleculeFormatError
from ..physical_constants import constants
from ..util import which_import

if TYPE_CHECKING:
    from ..models.v2 import Molecule

__all__ = ["from_mae", "to_mae"]


_MAE_CHARGE_PROPERTY = "i_m_Molecular_charge"
_MAE_MULTIPLICITY_PROPERTY = "i_m_Spin_multiplicity"


def _import_schrodinger():
    r"""Import the optional Schrodinger modules needed for Maestro I/O.

    Returns
    -------
    tuple[module, module]
        The :mod:`schrodinger.structure` and :mod:`schrodinger.infra.mm`
        modules, respectively.

    Raises
    ------
    ModuleNotFoundError
        If the Schrodinger Python modules are unavailable.
    """
    which_import(
        "schrodinger.structure",
        raise_error=True,
        raise_msg="Maestro support requires a Schrodinger Python environment.",
    )

    from schrodinger import structure
    from schrodinger.infra import mm

    return structure, mm


def _validate_mae_path(filename: str | PathLike[str]) -> Path:
    r"""Validate and normalize a Maestro file path.

    Parameters
    ----------
    filename
        Path whose filename must end in ``.mae`` or ``.maegz``, case-insensitively.

    Returns
    -------
    Path
        The normalized path object.

    Raises
    ------
    ValueError
        If the filename does not have a supported Maestro extension.
    """
    path = Path(filename)
    lower_name = path.name.lower()
    if not lower_name.endswith((".mae", ".maegz")):
        raise ValueError(f"Maestro filename must end in .mae or .maegz: {filename}")
    return path


def _coerce_bond_order(order: float, permissive: bool) -> tuple[int, bool]:
    r"""Convert a QCSchema bond order to an order supported by Maestro.

    Parameters
    ----------
    order
        QCSchema bond order to convert.
    permissive
        If ``True``, round half up and clamp unsupported orders to Maestro's
        inclusive range from zero through three. If ``False``, reject
        unsupported orders.

    Returns
    -------
    tuple[int, bool]
        The Maestro bond order and whether the input required a lossy
        conversion.

    Raises
    ------
    ValueError
        If ``order`` is non-finite, or if it is unsupported and
        ``permissive`` is ``False``.
    """
    value = float(order)
    if not math.isfinite(value):
        raise ValueError(f"Bond order must be finite, not {order!r}.")

    rounded = math.floor(value + 0.5)
    if value == rounded and 0 <= rounded <= 3:
        return rounded, False

    if not permissive:
        raise ValueError(
            f"Maestro supports integer bond orders from 0 through 3, not {order!r}. "
            "Pass permissive=True to round to the nearest supported order."
        )

    return min(max(rounded, 0), 3), True


def from_mae(filename: str | PathLike[str]) -> list[Molecule]:
    r"""Read Maestro structures as QCSchema v2 Molecules.

    Coordinates are converted from angstrom to bohr. Elemental atoms carrying
    Maestro's counterpoise property become QCSchema ghost atoms with
    ``real=False``. Unsupported non-counterpoise dummy atoms are omitted with
    a warning.

    Atom- and bond-level properties without QCSchema Molecule equivalents
    are intentionally ignored.

    Parameters
    ----------
    filename
        Maestro file in ``.mae`` or ``.maegz`` format.

    Returns
    -------
    list[Molecule]
        One QCSchema v2 Molecule for each structure in the Maestro file.
    """
    from ..models.v2 import Molecule

    path = _validate_mae_path(filename)
    structure, mm = _import_schrodinger()

    molecules = []
    with structure.StructureReader(path) as reader:
        for mae_structure in reader:
            symbols = []
            geometry = []
            real = []
            atomic_numbers = []
            atom_index_map = {}
            dummy_indices = []
            for atom in mae_structure.atom:
                is_counterpoise = bool(atom.property.get(mm.M2IO_DATA_ATOM_COUNTERPOISE, 0))
                if atom.atomic_number <= 0 and not is_counterpoise:
                    dummy_indices.append(atom.index)
                    continue

                atom_index_map[atom.index] = len(symbols)
                symbols.append(atom.element)
                geometry.append(atom.xyz)
                real.append(not is_counterpoise)
                atomic_numbers.append(atom.atomic_number)

            if dummy_indices:
                warnings.warn(
                    "Maestro dummy atoms are not supported and were omitted at indices "
                    + ", ".join(map(str, dummy_indices)),
                    UserWarning,
                    stacklevel=2,
                )

            connectivity = [
                (atom_index_map[bond.atom1.index], atom_index_map[bond.atom2.index], bond.order)
                for bond in mae_structure.bond
                if bond.order is not None and bond.atom1.index in atom_index_map and bond.atom2.index in atom_index_map
            ]

            molecular_charge = mae_structure.property.get(_MAE_CHARGE_PROPERTY, mae_structure.formal_charge)
            molecular_multiplicity = mae_structure.property.get(_MAE_MULTIPLICITY_PROPERTY)
            if molecular_multiplicity is None:
                electron_count = sum(number for number, is_real in zip(atomic_numbers, real) if is_real)
                electron_count -= molecular_charge
                molecular_multiplicity = int(round(electron_count)) % 2 + 1

            molecules.append(
                Molecule(
                    symbols=symbols,
                    geometry=np.asarray(geometry) / constants.bohr2angstroms,
                    name=mae_structure.title or None,
                    molecular_charge=molecular_charge,
                    molecular_multiplicity=molecular_multiplicity,
                    real=real,
                    connectivity=connectivity or None,
                )
            )

    if not molecules:
        raise MoleculeFormatError(f"Maestro file contains no structures: {path}")
    return molecules


def to_mae(
    molecule: Molecule | Mapping[str, Any],
    filename: str | PathLike[str],
    *,
    overwrite: bool = True,
    permissive: bool = False,
) -> None:
    r"""Write a QCSchema Molecule to a Maestro structure file.

    Parameters
    ----------
    molecule
        A QCSchema Molecule model or mapping. Coordinates are interpreted as
        bohr.
    filename
        Maestro file in ``.mae`` or ``.maegz`` format.
    overwrite
        Overwrite an existing file. When ``False``, append the structure.
    permissive
        Round unsupported QCSchema bond orders to the nearest Maestro order
        from 0 through 3. A warning describes every lossy conversion. By
        default, unsupported bond orders raise ``ValueError``.

    Notes
    -----
    QCSchema counterpoise atoms retain their element and receive Maestro's
    ``i_m_counterpoise`` property. Arbitrary QCSchema extras and Maestro
    visualization properties are not written.
    """
    from ..models.v2 import Molecule

    path = _validate_mae_path(filename)
    structure, mm = _import_schrodinger()

    if isinstance(molecule, Mapping):
        molecule = Molecule(**molecule)
    elif not all(
        hasattr(molecule, field)
        for field in (
            "symbols",
            "geometry",
            "real",
            "molecular_charge",
            "molecular_multiplicity",
            "connectivity",
        )
    ):
        raise TypeError("molecule must be a QCSchema Molecule model or mapping.")

    molecular_charge = float(molecule.molecular_charge)
    molecular_multiplicity = float(molecule.molecular_multiplicity)
    if not molecular_charge.is_integer():
        raise ValueError(f"Maestro requires an integer molecular charge, not {molecular_charge!r}.")
    if not molecular_multiplicity.is_integer():
        raise ValueError(f"Maestro requires an integer molecular multiplicity, not {molecular_multiplicity!r}.")

    mae_structure = structure.create_new_structure()
    geometry = np.asarray(molecule.geometry) * constants.bohr2angstroms
    for symbol, xyz, is_real in zip(molecule.symbols, geometry, molecule.real):
        atom = mae_structure.addAtom(str(symbol), *map(float, xyz))
        if not is_real:
            atom.property[mm.M2IO_DATA_ATOM_COUNTERPOISE] = 1

    lossy_bonds = []
    for atom1, atom2, order in molecule.connectivity or []:
        mae_order, was_rounded = _coerce_bond_order(order, permissive)
        mae_structure.addBond(int(atom1) + 1, int(atom2) + 1, mae_order)
        if was_rounded:
            lossy_bonds.append(f"({atom1}, {atom2}) {order} -> {mae_order}")

    if lossy_bonds:
        warnings.warn(
            "Rounded unsupported bond orders for Maestro output: " + ", ".join(lossy_bonds),
            UserWarning,
            stacklevel=2,
        )

    if molecule.name:
        mae_structure.title = molecule.name
    mae_structure.property[_MAE_CHARGE_PROPERTY] = int(molecular_charge)
    mae_structure.property[_MAE_MULTIPLICITY_PROPERTY] = int(molecular_multiplicity)

    with structure.StructureWriter(path, overwrite=overwrite) as writer:
        writer.append(mae_structure)
