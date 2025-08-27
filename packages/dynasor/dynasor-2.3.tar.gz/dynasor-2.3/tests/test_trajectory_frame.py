import pytest
import numpy as np
from dynasor.trajectory.trajectory_frame import TrajectoryFrame
from dynasor.trajectory import Trajectory


def test_get_as_arrays():

    # setup
    atomic_indices_ref = dict()
    atomic_indices_ref['Cs'] = np.array([0, 1, 2, 3, 4, 9])
    atomic_indices_ref['Pb'] = np.array([5, 6, 7, 8])
    positions_ref = np.arange(0, 30, 1).reshape((10, 3))
    velocities_ref = np.arange(-15, 15, 1).reshape((10, 3))
    frame = TrajectoryFrame(atomic_indices_ref, 0, positions_ref, velocities_ref)

    # get arrays with complete atomic_indices
    assert np.allclose(frame.get_positions_as_array(atomic_indices_ref), positions_ref)
    assert np.allclose(frame.get_velocities_as_array(atomic_indices_ref), velocities_ref)

    # ValueError with incomplete atomic_indices, len(all_inds) != n_atoms
    atomic_indices = dict()
    atomic_indices['Cs'] = [0, 1, 2, 3, 4]
    atomic_indices['Pb'] = [5, 6, 7, 8]

    with pytest.raises(ValueError):
        frame.get_positions_as_array(atomic_indices)
    with pytest.raises(ValueError):
        frame.get_velocities_as_array(atomic_indices)

    # ValueError with incomplete atomic_indices, len(set(all_inds)) != n_atoms
    atomic_indices = dict()
    atomic_indices['Cs'] = [0, 1, 2, 3, 4, 4]
    atomic_indices['Pb'] = [5, 6, 7, 8]

    with pytest.raises(ValueError):
        frame.get_positions_as_array(atomic_indices)
    with pytest.raises(ValueError):
        frame.get_velocities_as_array(atomic_indices)


def test_str():
    atomic_indices = dict()
    atomic_indices['Cs'] = np.arange(0, 20)
    atomic_indices['Pb'] = np.arange(50, 100)

    # No velocities
    traj = Trajectory('tests/trajectory_reader/trajectory_files/dump.xyz',
                      trajectory_format='extxyz', atomic_indices=atomic_indices)
    str_target = 'Frame index 0\n  positions  : Cs   shape : (20, 3)\n'\
                 '  positions  : Pb   shape : (50, 3)'
    frame = next(traj)
    assert str(frame) == str_target

    # With velocities
    traj = Trajectory('tests/trajectory_reader/trajectory_files/dump_long_with_velocities.xyz',
                      trajectory_format='extxyz', atomic_indices=atomic_indices)

    str_target = 'Frame index 0\n  positions  : Cs   shape : (20, 3)\n'\
                 '  positions  : Pb   shape : (50, 3)\n'\
                 '  velocities : Cs   shape : (20, 3)\n  velocities : Pb   shape : (50, 3)'
    frame = next(traj)
    assert str(frame) == str_target


def test_read_indices_from_trajectory():
    # Check that error is raised when trying to read atomic_indices from reader and file type
    # combination that doesn't support this
    with pytest.raises(ValueError, match='Could not read atomic indices from the trajectory.'):
        traj = Trajectory('tests/trajectory_reader/trajectory_files/water_10snapshots.xtc',
                          trajectory_format='xtc', atomic_indices='read_from_trajectory')

    # Check that error is raised when trying to read atomic_indices from the internal lammps reader,
    # that doesn't have this functionality
    with pytest.raises(ValueError, match='Could not read atomic indices from the trajectory.'):
        traj = Trajectory('tests/trajectory_reader/trajectory_files/positions.lammpstrj',
                          trajectory_format='lammps_internal',
                          atomic_indices='read_from_trajectory')

    # Check that atomic indices are passed to the trajectory frame from the MDAnalysis reader
    traj = Trajectory('tests/trajectory_reader/trajectory_files/positions.lammpstrj',
                      trajectory_format='lammps_mdanalysis', length_unit='Angstrom',
                      time_unit='ps', atomic_indices='read_from_trajectory')
    assert isinstance(traj.atomic_indices, dict)
    assert np.all(traj.atomic_indices['1'] == [0,  3,  6,  9, 12, 15, 18, 21])
    assert np.all(traj.atomic_indices['2'] == [1,  2,  4,  5,  7,  8, 10, 11,
                                               13, 14, 16, 17, 19, 20, 22, 23])

    # Check that atomic indices are passed to the trajectory frame from the Extxyz reader
    traj = Trajectory('tests/trajectory_reader/trajectory_files/dump.xyz',
                      trajectory_format='extxyz', length_unit='Angstrom',
                      time_unit='ps', atomic_indices='read_from_trajectory')
    assert isinstance(traj.atomic_indices, dict)
    assert np.all(traj.atomic_indices['Cs'] == np.arange(0, 1080, 5))
    assert np.all(traj.atomic_indices['Pb'] == np.arange(1, 1080, 5))
