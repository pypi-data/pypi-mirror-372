from typing import Optional

import numpy as np

from ase import Atoms
from numpy.typing import NDArray

from dynasor.logging_tools import logger
from dynasor.trajectory import Trajectory
from dynasor.tools.structures import get_displacements_from_u


def project_modes(
    traj: Trajectory,
    modes: NDArray[float],
    ideal_supercell: Atoms,
    check_mic: Optional[bool] = True,
) -> tuple[NDArray[float], NDArray[float]]:
    """Projects an atomic trajectory onto set of phonon modes.

    Parameters
    ----------
    traj
        Input trajectory.
    modes
        Modes to project on `(1, Nlambda, N, 3)` array where `Nm` is the number of modes
        and `N` is the number of atoms in the supercell.
    ideal_supercell
        Ideal supercell used to find atomic displacements and should correspond to the ideal
        structure. Be careful not to mess up the permutation.
    check_mic
        Whether to wrap the displacements or not, faster if no wrap.

    Returns
    -------
        A tuple comprising `(Q,P)` where `Q` are the mode coordinates as a complex array
        with dimension (length of traj, number of modes) and `P` are the  mode momenta as a
        complex array with dimension (length of traj, number of modes).
    """
    # logger
    logger.info('Running mode projection')

    modes = np.array(modes)

    original_mode_shape = modes.shape

    if modes.shape[-2] != traj.n_atoms:
        raise ValueError('Second dim in modes must be same len as number of atoms in trajectory')
    if traj.n_atoms != len(ideal_supercell):
        raise ValueError('ideal_supercell must contain the same number of atoms as the trajectory.')

    modes = modes.reshape((-1, modes.shape[-2], 3))

    Q_traj, P_traj = [], []
    for it, frame in enumerate(traj):
        logger.debug(f'Reading frame {it}')

        # Make positions into displacements
        x = frame.get_positions_as_array(traj._atomic_indices)
        u = x - ideal_supercell.positions

        # Calculate Q
        u = get_displacements_from_u(u, ideal_supercell.cell, check_mic=check_mic)
        Q = np.einsum('mnx,nx->m', modes, u)

        # Calculate P
        if frame.velocities_by_type is not None:
            v = frame.get_velocities_as_array(traj._atomic_indices)
            P = np.einsum('mna,na->m', modes.conj(), v)
        else:
            P = np.zeros_as(Q)

        Q_traj.append(Q)
        P_traj.append(P)

    Q_traj = Q_traj.reshape((len(Q_traj), *original_mode_shape[:-2]))
    P_traj = P_traj.reshape((len(P_traj), *original_mode_shape[:-2]))

    return np.array(Q_traj), np.array(P_traj)
