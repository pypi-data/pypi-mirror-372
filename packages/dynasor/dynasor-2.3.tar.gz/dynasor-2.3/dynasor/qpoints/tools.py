import itertools
from fractions import Fraction

import numpy as np
from numpy.typing import NDArray

from dynasor.modes.tools import inv


def get_supercell_qpoints_along_path(
        path: list[tuple[str, str]],
        coordinates: dict[str, NDArray[float]],
        primitive_cell: NDArray[float],
        super_cell: NDArray[float]) -> list[NDArray[float]]:
    r"""
    Returns the q-points commensurate with the given supercell along the specific path.

    Parameters
    ----------
    path
        List of pairs of q-point labels.
    coordinates
        Dict with q-point labels and coordinates as keys and values, respectively;
        there must be one entry for each q-point label used in :attr:`path`.
    primitive_cell
        Cell metric of the primitive cell with lattice vectors as rows.
    super_cell
        Cell metric of the supercell with lattice vectors as rows.

    Returns
    -------
        A list of the accessible q-point coordinates along the specified segment.

    Example
    --------
    The following example illustrates how to retrieve the q-points that
    can be sampled using a supercell comprising :math:`6 \times 6 \times 6`
    conventional (4-atom) unit cells of FCC Al along the path X-:math:`\Gamma`-L.

    >>> import numpy as np
    >>> from ase.build import bulk
    >>> from dynasor.qpoints import get_supercell_qpoints_along_path
    >>> prim = bulk('Al', 'fcc', a=4.0)
    >>> supercell = bulk('Al', 'fcc', a=4.0, cubic=True).repeat(6)
    >>> path = [('X', 'G'), ('G', 'L'), ('L', 'W')]
    >>> coordinates = dict(X=[0.5, 0.5, 0], G=[0, 0, 0],
    ...                    L=[0.5, 0.5, 0.5], W=[0.5, 0.25, 0.75])
    >>> qpoints = get_supercell_qpoints_along_path(
    ...     path, coordinates, prim.cell, supercell.cell)

    """
    from .lattice import Lattice
    lat = Lattice(primitive_cell, super_cell)

    for lbl in np.array(path).flatten():
        if lbl not in coordinates:
            raise ValueError(f'Unknown point in path: {lbl}')

    # build the segments
    supercell_paths = []
    for k, (l1, l2) in enumerate(path):
        q1 = np.array(coordinates[l1], dtype=float)
        q2 = np.array(coordinates[l2], dtype=float)
        dynasor_path, _ = lat.make_path(q1, q2)
        supercell_paths.append(dynasor_path)
    return supercell_paths


def find_on_line(
    start: NDArray[float],
    stop: NDArray[float],
    P: NDArray[int],
) -> set[NDArray[float]]:
    """Find fractional distances between start and stop combatible with P.

    A supercell is defined by `P @ c = S` for some repetition matrix `P` and we
    want to find fractions so that::

        [start + f * (stop - start)] @ P = n

    Parameters
    ----------
    start
        Start of line in reduced supercell coordinates.
    stop
        End of line in reduced supercell coordinates.
    P
        Repetion matrix defining the supercell.
    """

    if np.allclose(start, stop):
        return [Fraction(0, 1)]

    start = np.array([Fraction(s).limit_denominator() for s in start])
    stop = np.array([Fraction(s).limit_denominator() for s in stop])

    A = start @ P
    B = (stop - start) @ P

    fracs = None
    for a, b in zip(A, B):
        fs = solve_Diophantine(a, b)
        if fs is None:  # "inf" solutions
            continue
        elif fs == []:  # No solutions
            return []
        fracs = set(fs) if fracs is None else fracs.intersection(fs)
    return sorted(fracs)


def solve_Diophantine(a: Fraction, b: Fraction) -> list[Fraction]:
    """Solve n = a + xb for all n in Z and a,b in Q such that 0 <= x <= 1."""

    if b == 0:
        if a.denominator == 1:
            return None
        else:
            return []

    if b < 0:
        right = np.ceil(a)
        left = np.floor(a + b)
    else:
        left = np.floor(a)
        right = np.ceil(a + b)

    ns = np.arange(left, right + 1)
    fracs = [Fraction(n - a, b) for n in ns]
    fracs = [f for f in fracs if 0 <= f <= 1]

    return fracs


def get_commensurate_lattice_points(P: NDArray[int]) -> NDArray[float]:
    """Return commensurate points for a supercell defined by repetition matrix `P`.

    Finds all `n` such that `n = f P` where `f` is between 0 and 1

    Parameters
    ----------
    P
        The repetion matrix relating the primitive and supercell.

    Returns
    -------
        The commensurate lattice points.
    """
    inv_P_matrix = inv(P, as_fraction=True)

    assert np.all(P @ inv_P_matrix == np.eye(3))

    n_max = np.where(P > 0, P, 0).sum(axis=0) + 1
    n_min = np.where(P < 0, P, 0).sum(axis=0)

    ranges = [np.arange(*n) for n in zip(n_min, n_max)]

    lattice_points = []
    for lp in itertools.product(*ranges):
        tmp = lp @ inv_P_matrix
        if np.all(tmp >= 0) and np.all(tmp < 1):
            lattice_points.append(lp)

    assert len(lattice_points) == len(set(lattice_points))
    lattice_points = np.array(lattice_points)
    return lattice_points
