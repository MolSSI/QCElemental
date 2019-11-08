from typing import List, Optional, Tuple, Union

import numpy as np

from ..covalent_radii import covalentradii
from ..exceptions import NotAnElementError

__all__ = ["guess_connectivity"]


def guess_connectivity(
    symbols: np.ndarray, geometry: np.ndarray, threshold: float = 1.2, default_connectivity: Optional[float] = None
) -> List[Union[Tuple[int, int], Tuple[int, int, float]]]:
    """
    Finds connected atoms based off of a covalent radii metric.

    Parameters
    ----------
    symbols : np.ndarray
        The molecular symbols (e.g., 'Zr', 'C')
    geometry : np.ndarray
        The molecular geometry in Bohr
    threshold : float, optional
        Tunes the covalent radii metric safety factor.
    default_connectivity : Optional[float], optional
        Provides a default connectivity value

    Returns
    -------
    List[Union[Tuple[int, int], Tuple[int, int, float]]]
        Provides a list of connected atoms, or optionally a list of
        connected atoms and default connectivity if provided.
    """

    geometry = np.asarray(geometry, dtype=float).reshape(-1, 3)
    radii = []
    for s in symbols:
        try:
            radii.append(covalentradii.get(s, missing=1.8))
        except NotAnElementError:
            radii.append(1.8)

    radii = np.array(radii)

    # Upper triangular
    con = []
    for x in range(geometry.shape[0]):
        diffs = geometry[x] - geometry[x + 1 :]
        dists = np.einsum("ij,ij->i", diffs, diffs)
        np.sqrt(dists, out=dists)

        cutoff = (radii[x] + radii[x + 1 :]) * threshold
        where = np.where(dists < cutoff)[0]
        where += x + 1

        for atom2 in where:
            con.append((x, atom2))

    if default_connectivity:
        con = [(x[0], x[1], default_connectivity) for x in con]

    return con
