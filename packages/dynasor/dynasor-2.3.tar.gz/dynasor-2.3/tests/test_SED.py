import os
import pytest
import numpy as np
from ase import Atoms
from dynasor.correlation_functions import compute_spectral_energy_density
from dynasor.trajectory import Trajectory


@pytest.fixture
def traj_fname_xyz():
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(this_dir, 'trajectory_reader/trajectory_files/dump.xyz')
    return traj_fname


@pytest.fixture
def traj_fname_xyz_with_velocities():
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(this_dir,
                              'trajectory_reader/trajectory_files/dump_with_velocities.xyz')
    return traj_fname


@pytest.fixture
def prim():
    alat = 6.0
    spos_A = np.array([0, 0, 0])
    spos_B = np.array([0.5, 0.5, 0.5])
    spos_X = np.array([[0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]])
    scaled_positions = np.vstack((spos_A, spos_B, spos_X))
    cell = alat * np.eye(3)
    types = ['Cs', 'Pb', 'Br', 'Br', 'Br']
    atoms = Atoms(pbc=True, cell=cell, scaled_positions=scaled_positions, symbols=types)
    return atoms


def test_sed(traj_fname_xyz_with_velocities, prim):

    # setup
    size = 6
    dt = 2.5
    traj = Trajectory(traj_fname_xyz_with_velocities, trajectory_format='extxyz')
    atoms_ideal = prim.repeat(size)
    q_points = np.array([a * np.array([2 * np.pi / 6.0, 0, 0]) for a in np.linspace(0, 1, size+1)])

    # run SED
    f, sed = compute_spectral_energy_density(traj, ideal_supercell=atoms_ideal,
                                             primitive_cell=prim, q_points=q_points, dt=dt)

    f_target = 1 / dt * 2 * np.pi * np.linspace(0, 1/2, 3)
    assert sed.shape == (7, 3)
    assert np.allclose(f, f_target)

    sed_target = np.array([
       [0.10847998, 0.18091865, 0.15408934],
       [0.23743116, 0.17269055, 0.29059788],
       [0.20541601, 0.21506601, 0.14684155],
       [0.12568888, 0.26424448, 0.33979104],
       [0.20541601, 0.17761411, 0.14684155],
       [0.23743116, 0.19715230, 0.29059788],
       [0.10847998, 0.18091865, 0.15408934]])

    assert np.allclose(sed, sed_target)

    # test with step > 1
    step = 2
    traj = Trajectory(traj_fname_xyz_with_velocities, trajectory_format='extxyz',
                      frame_step=step)
    f, sed = compute_spectral_energy_density(traj, ideal_supercell=atoms_ideal,
                                             primitive_cell=prim, q_points=q_points, dt=dt)

    f_target = 1 / (dt*step) * 2 * np.pi * np.linspace(0, 1/2, 2)
    assert sed.shape == (7, 2)
    assert np.allclose(f, f_target)


def test_sed_without_velocities(traj_fname_xyz, prim):
    size = 6
    dt = 2.5
    atoms_ideal = prim.repeat(size)
    q_points = np.array([a * np.array([2 * np.pi / 6.0, 0, 0]) for a in np.linspace(0, 1, size+1)])
    traj = Trajectory(traj_fname_xyz, trajectory_format='extxyz')
    with pytest.raises(ValueError):
        f, sed = compute_spectral_energy_density(traj, ideal_supercell=atoms_ideal,
                                                 primitive_cell=prim, q_points=q_points, dt=dt)


def test_sed_with_incorrect_supercell(traj_fname_xyz, prim):
    size = 6
    dt = 2.5
    atoms_ideal = prim.repeat(size)
    del atoms_ideal[0]
    q_points = np.array([a * np.array([2 * np.pi / 6.0, 0, 0]) for a in np.linspace(0, 1, size+1)])
    traj = Trajectory(traj_fname_xyz, trajectory_format='extxyz')
    with pytest.raises(ValueError, match='ideal_supercell must contain the same number of atoms'
                                         ' as the trajectory'):
        f, sed = compute_spectral_energy_density(traj, ideal_supercell=atoms_ideal,
                                                 primitive_cell=prim, q_points=q_points, dt=dt)
