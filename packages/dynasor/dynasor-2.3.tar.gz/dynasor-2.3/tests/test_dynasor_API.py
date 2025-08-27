import os

import numpy as np
import pytest

from dynasor.correlation_functions import (
    compute_dynamic_structure_factors,
    compute_static_structure_factors,
)
from dynasor.sample import Sample
from dynasor.trajectory import Trajectory


@pytest.fixture
def traj_fname_xyz():
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(this_dir,
                              'trajectory_reader/trajectory_files/dump_with_velocities.xyz')
    return traj_fname


@pytest.fixture
def traj_fname_lammps():
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(
        this_dir,
        'trajectory_reader/trajectory_files/positions.lammpstrj')
    return traj_fname


@pytest.fixture
def q_points():
    q_points = np.array([i * np.array([1/2, 2/3, 1.235]) for i in np.linspace(0, 10, 11)])
    return q_points


def test_API_dynamic_structure_factor(traj_fname_xyz, q_points):
    traj = Trajectory(traj_fname_xyz, 'extxyz')
    res = compute_dynamic_structure_factors(traj, q_points=q_points, dt=1.0, window_size=4)
    assert isinstance(res, Sample)


def test_API_dynamic_structure_factor_selfpart(traj_fname_xyz, q_points):
    traj = Trajectory(traj_fname_xyz, 'extxyz')
    res = compute_dynamic_structure_factors(traj, q_points=q_points, dt=1.0, window_size=4,
                                            calculate_incoherent=True)
    assert isinstance(res, Sample)


def test_API_static_structure_factor(traj_fname_xyz_long, q_points):
    # setup
    n_atoms = 320
    n_A = 50
    atomic_indices = dict()
    atomic_indices['A'] = np.arange(0, n_A, 1)
    atomic_indices['B'] = np.arange(n_A, n_atoms, 1)

    # calculate static
    traj = Trajectory(
        traj_fname_xyz_long, trajectory_format='extxyz', atomic_indices=atomic_indices)
    res1 = compute_static_structure_factors(traj, q_points=q_points)
    assert res1.simulation_data['number_of_frames'] == 30

    # calculate S(q) via compute_dynamic_structure_factors (use dummy dt and window_size)
    traj = Trajectory(
        traj_fname_xyz_long, trajectory_format='extxyz', atomic_indices=atomic_indices)
    res2 = compute_dynamic_structure_factors(traj, q_points=q_points, dt=1.0, window_size=4)
    assert res2.simulation_data['number_of_frames'] == 30

    # compare results
    pairs = ['A_A', 'A_B', 'B_B']
    for pair in pairs:
        Sq1 = getattr(res1, f'Sq_{pair}')
        Sq2 = getattr(res2, f'Fqt_coh_{pair}')[:, 0].reshape(-1, 1)
        assert np.allclose(Sq1, Sq2)
    assert np.allclose(res1.Sq, res2.Fqt_coh[:, 0].reshape(-1, 1))


# Comparing the mdanalysis lammps reader to the internal lammps reader
def test_API_calling_mdanalysis_reader(traj_fname_lammps, q_points):
    window = 4
    dt = 1.0

    traj1 = Trajectory(traj_fname_lammps, 'lammps_internal')
    traj2 = Trajectory(traj_fname_lammps, 'lammps_mdanalysis',
                       length_unit='Angstrom', time_unit='fs')

    res1 = compute_dynamic_structure_factors(traj1, q_points=q_points, dt=dt, window_size=window)
    res2 = compute_dynamic_structure_factors(traj2, q_points=q_points, dt=dt, window_size=window)
    assert isinstance(res1, Sample)
    assert isinstance(res2, Sample)

    # check that results are the same
    assert res1.available_correlation_functions == res2.available_correlation_functions
    for key in res1.available_correlation_functions:
        np.testing.assert_almost_equal(res1[key], res2[key], decimal=5)


# test of time-sampling parameters
# --------------------------------
def test_API_dynamic_step(traj_fname_xyz_long, q_points):
    """
    Ensure that setting step > 1 affects the resulting time
    """
    dt = 1.0
    time_window = 4
    step = 1

    for step in [1, 2, 3]:

        traj = Trajectory(traj_fname_xyz_long, 'extxyz', frame_step=step)
        res = compute_dynamic_structure_factors(
            traj, q_points=q_points, dt=dt, window_size=time_window)
        assert isinstance(res, Sample)
        time = res.time
        assert np.allclose(np.diff(time), step * dt), (np.diff(time), step * dt)


# test ValueErrors from bad input arguments
# -----------------------------------------

def test_raises_with_bad_input_args(traj_fname_xyz_long, q_points):
    time_window = 4
    dt = 1.0

    # q-points wrong shape
    traj = Trajectory(traj_fname_xyz_long, 'extxyz')
    with pytest.raises(ValueError, match=r'q-points array has the wrong shape'):
        compute_dynamic_structure_factors(traj, q_points=q_points[:, 1:], dt=dt,
                                          window_size=time_window)

    traj = Trajectory(traj_fname_xyz_long, 'extxyz')
    with pytest.raises(ValueError, match=r'q-points array has the wrong shape'):
        compute_static_structure_factors(traj, q_points=q_points[:, 1:])

    # dt not positive
    traj = Trajectory(traj_fname_xyz_long, 'extxyz')
    with pytest.raises(ValueError, match=r'dt must be positive'):
        compute_dynamic_structure_factors(traj, q_points=q_points, dt=-1.0, window_size=time_window)

    # bad window_size
    traj = Trajectory(traj_fname_xyz_long, 'extxyz')
    with pytest.raises(ValueError, match=r'window_size must be larger than 2'):
        compute_dynamic_structure_factors(traj, q_points=q_points, dt=dt, window_size=1)

    traj = Trajectory(traj_fname_xyz_long, 'extxyz')
    with pytest.raises(ValueError, match=r'window_size must be even'):
        compute_dynamic_structure_factors(traj, q_points=q_points, dt=dt, window_size=5)

    # bad window_step
    traj = Trajectory(traj_fname_xyz_long, 'extxyz')
    with pytest.raises(ValueError, match=r'window_step must be positive'):
        compute_dynamic_structure_factors(traj, q_points=q_points, dt=dt, window_size=time_window,
                                          window_step=-1)
