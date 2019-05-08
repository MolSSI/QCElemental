import math
import re
from typing import Dict, List

import numpy as np

from ..physical_constants import constants


def distance_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Euclidean distance matrix between rows of arrays `a` and `b`. Equivalent to
    `scipy.spatial.distance.cdist(a, b, 'euclidean')`. Returns a.shape[0] x b.shape[0] array.

    """
    assert a.shape[1] == b.shape[1], """Inner dimensions do not match"""
    distm = np.zeros([a.shape[0], b.shape[0]])
    for i in range(a.shape[0]):
        distm[i] = np.linalg.norm(a[i] - b, axis=1)
    return distm


def update_with_error(a: Dict, b: Dict, path=None) -> Dict:
    """Merges `b` into `a` like dict.update; however, raises KeyError if values of a
    key shared by `a` and `b` conflict.

    Adapted from: https://stackoverflow.com/a/7205107

    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                update_with_error(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif a[key] is None:
                a[key] = b[key]
            elif (isinstance(a[key], (list, tuple)) and
                  not isinstance(a[key], str) and
                  isinstance(b[key], (list, tuple)) and
                  not isinstance(b[key], str) and
                  len(a[key]) == len(b[key]) and
                  all((av is None or av == bv) for av, bv in zip(a[key], b[key]))):  # yapf: disable
                a[key] = b[key]
            else:
                raise KeyError('Conflict at {}: {} vs. {}'.format('.'.join(path + [str(key)]), a[key], b[key]))
        else:
            a[key] = b[key]
    return a


def standardize_efp_angles_units(units: str, geom_hints: List[List[float]]) -> List[List[float]]:
    """Applies to the pre-validated xyzabc or points hints in `geom_hints`
    the libefp default (1) units of [a0] and (2) radian angle range of
    (-pi, pi]. The latter is handy since this is how libefp returns hints

    """

    def radrge(radang):
        """Adjust `radang` by 2pi into (-pi, pi] range."""
        if radang > math.pi:
            return radang - 2 * math.pi
        elif radang <= -math.pi:
            return radang + 2 * math.pi
        else:
            return radang

    if units == 'Angstrom':
        iutau = 1. / constants.bohr2angstroms
    else:
        iutau = 1.

    hints = []
    for hint in geom_hints:
        if len(hint) == 6:
            x, y, z = [i * iutau for i in hint[:3]]
            a, b, c = [radrge(i) for i in hint[3:]]
            hints.append([x, y, z, a, b, c])
        if len(hint) == 9:
            points = [i * iutau for i in hint]
            hints.append(points)

    return hints


def filter_comments(string: str) -> str:
    """Remove from `string` any Python-style comments ('#' to end of line)."""

    return re.sub(r'(^|[^\\])#.*', '', string)


def unnp(dicary: Dict, _path=None, *, flat: bool=False) -> Dict:
    """Return `dicary` with any ndarray values replaced by lists.

    Parameters
    ----------
    dicary: dict
        Dictionary where any internal iterables are dict or list.
    flat : bool, optional
        Whether the returned lists are flat or nested.

    Returns
    -------
    dict
        Input with any ndarray values replaced by lists.

    """
    if _path is None:
        _path = []

    ndicary = {}
    for k, v in dicary.items():
        if isinstance(v, dict):
            ndicary[k] = unnp(v, _path + [str(k)], flat=flat)
        elif isinstance(v, list):
            # relying on Py3.6+ ordered dict here
            fakedict = {kk: vv for kk, vv in enumerate(v)}
            tolisted = unnp(fakedict, _path + [str(k)], flat=flat)
            ndicary[k] = list(tolisted.values())
        else:
            try:
                v.shape
            except AttributeError:
                ndicary[k] = v
            else:
                if flat:
                    ndicary[k] = v.ravel().tolist()
                else:
                    ndicary[k] = v.tolist()
    return ndicary


def _norm(points) -> float:
    """
    Return the Frobenius norm across axis=-1, NumPy's internal norm is crazy slow (~4x)
    """

    tmp = np.atleast_2d(points)
    return np.sqrt(np.einsum("ij,ij->i", tmp, tmp))


def measure_coordinates(coordinates, measurements, degrees=False):
    """
    Measures a geometry array based on 0-based indices provided, automatically detects distance, angle,
    and dihedral based on length of measurement input.
    """

    coordinates = np.atleast_2d(coordinates)
    num_coords = coordinates.shape[0]

    single = False
    if isinstance(measurements[0], int):
        measurements = [measurements]
        single = True

    ret = []
    for num, m in enumerate(measurements):
        if any(x >= num_coords for x in m):
            raise ValueError("An index of measurement {} is out of bounds.".format(num))

        kwargs = {}
        if len(m) == 2:
            func = compute_distance
        elif len(m) == 3:
            func = compute_angle
            kwargs = {"degrees": degrees}
        elif len(m) == 4:
            func = compute_dihedral
            kwargs = {"degrees": degrees}
        else:
            raise KeyError(f"Unrecognized number of arguments for measurement {num}, found {len(m)}, expected 2-4.")

        val = func(*[coordinates[x] for x in m], **kwargs)
        ret.append(float(val))

    if single:
        return ret[0]
    else:
        return ret


def compute_distance(points1, points2) -> np.ndarray:
    """
    Computes the distance between the provided points on a per-row basis.

    Parameters
    ----------
    points1 : array-like
        The first list of points, can be 1D or 2D
    points2 : array-like
        The second list of points, can be 1D or 2D

    Returns
    -------
    distances : np.ndarray
        The array of distances between points1 and points2

    Notes
    -----
    Units are not considered inside these expressions, please preconvert to the same units before using.

    See Also
    --------
    distance_matrix
        Computes the distance between the provided points in all rows.
        compute_distance result is the diagonal of the distance_matrix result.

    """
    points1 = np.atleast_2d(points1)
    points2 = np.atleast_2d(points2)

    return _norm(points1 - points2)


def compute_angle(points1, points2, points3, *, degrees: bool=False) -> np.ndarray:
    """
    Computes the angle (p1, p2 [vertex], p3) between the provided points on a per-row basis.

    Parameters
    ----------
    points1 : np.ndarray
        The first list of points, can be 1D or 2D
    points2 : np.ndarray
        The second list of points, can be 1D or 2D
    points3 : np.ndarray
        The third list of points, can be 1D or 2D
    degrees : bool, options
        Returns the angle in degrees rather than radians if True

    Returns
    -------
    angles : np.ndarray
        The angle between the three points in radians

    Notes
    -----
    Units are not considered inside these expressions, please preconvert to the same units before using.
    """

    points1 = np.atleast_2d(points1)
    points2 = np.atleast_2d(points2)
    points3 = np.atleast_2d(points3)

    v12 = points1 - points2
    v23 = points2 - points3

    denom = _norm(v12) * _norm(v23)
    cosine_angle = np.einsum("ij,ij->i", v12, v23) / denom

    angle = np.pi - np.arccos(cosine_angle)

    if degrees:
        return np.degrees(angle)
    else:
        return angle


def compute_dihedral(points1, points2, points3, points4, *, degrees: bool=False) -> np.ndarray:
    """
    Computes the dihedral angle (p1, p2, p3, p4) between the provided points on a per-row basis using the Praxeolitic formula.

    Parameters
    ----------
    points1 : np.ndarray
        The first list of points, can be 1D or 2D
    points2 : np.ndarray
        The second list of points, can be 1D or 2D
    points3 : np.ndarray
        The third list of points, can be 1D or 2D
    points4 : np.ndarray
        The third list of points, can be 1D or 2D
    degrees : bool, options
        Returns the dihedral angle in degrees rather than radians if True

    Returns
    -------
    dihedrals : np.ndarray
        The dihedral angle between the four points in radians

    Notes
    -----
    Units are not considered inside these expressions, please preconvert to the same units before using.
    """

    # FROM: https://stackoverflow.com/questions/20305272/

    points1 = np.atleast_2d(points1)
    points2 = np.atleast_2d(points2)
    points3 = np.atleast_2d(points3)
    points4 = np.atleast_2d(points4)

    # Build the three vectors
    v1 = -1.0 * (points2 - points1)
    v2 = points3 - points2
    v3 = points4 - points3

    # Normalize the central vector
    v2 = v2 / _norm(v2)

    # v = projection of b0 onto plane perpendicular to b1
    #   = b0 minus component that aligns with b1
    # w = projection of b2 onto plane perpendicular to b1
    #   = b2 minus component that aligns with b1
    v = v1 - np.einsum("ij,ij->i", v1, v1) * v2
    w = v3 - np.einsum("ij,ij->i", v3, v2) * v2

    # angle between v and w in a plane is the torsion angle
    # v and w may not be normalized but that's fine since tan is y/x
    x = np.einsum("ij,ij->i", v, w)
    y = np.einsum("ij,ij->i", np.cross(v2, v), w)
    angle = np.arctan2(y, x)

    if degrees:
        return np.degrees(angle)
    else:
        return angle
