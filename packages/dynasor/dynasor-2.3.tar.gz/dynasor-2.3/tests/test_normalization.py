import os
import numpy as np
from dynasor.qpoints import get_spherical_qpoints
from dynasor.correlation_functions import compute_dynamic_structure_factors
from dynasor.correlation_functions import compute_static_structure_factors
from dynasor.trajectory import Trajectory


def test_normalization_dynamic_structure_factor():

    # traj index files
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(
        this_dir, 'trajectory_reader/trajectory_files/dump_long_with_velocities.xyz')
    index_fname = os.path.join(this_dir, 'trajectory_reader/trajectory_files/index_file_dump_long')

    # input parameters
    time_window = 4
    dt = 100
    q_max = 40
    max_points = 500

    # setup
    traj_format = 'extxyz'
    traj = Trajectory(traj_fname, trajectory_format=traj_format)
    q_points = get_spherical_qpoints(traj.cell, q_max=q_max, max_points=max_points)

    # run only total
    sample1 = compute_dynamic_structure_factors(traj, q_points, dt=dt, window_size=time_window,
                                                calculate_currents=True, calculate_incoherent=True)
    record = sample1.history[0]
    assert record['func'] == 'compute_dynamic_structure_factors'
    assert record['dt'] == 100
    assert record['window_size'] == 4
    assert record['window_step'] == 1
    assert 'date_time' in record

    # run with partial
    traj = Trajectory(traj_fname, trajectory_format=traj_format, atomic_indices=index_fname)
    sample2 = compute_dynamic_structure_factors(traj, q_points, dt=dt, window_size=time_window,
                                                calculate_currents=True, calculate_incoherent=True)

    # test Fqt
    F_tot1 = sample1.Fqt_coh_X_X
    F_tot2 = sample2.Fqt_coh
    assert np.allclose(F_tot1, F_tot2)

    pairs = ['Cs_Cs', 'Br_Br', 'Pb_Pb', 'Cs_Pb', 'Br_Cs', 'Br_Pb']
    F_tot_from_partials = np.zeros_like(F_tot1)
    for pair in pairs:
        F_tot_from_partials += getattr(sample2, f'Fqt_coh_{pair}')
    assert np.allclose(F_tot1, F_tot_from_partials)

    # test CL
    Cl_tot = sample1.Clqt_X_X
    Cl_tot_from_partials = np.zeros_like(Cl_tot)
    for pair in pairs:
        Cl_tot_from_partials += getattr(sample2, f'Clqt_{pair}')
    assert np.allclose(Cl_tot, Cl_tot_from_partials), np.max(np.abs(Cl_tot - Cl_tot_from_partials))

    # test Ct
    Ct_tot = sample1.Ctqt_X_X
    Ct_tot_from_partials = np.zeros_like(Ct_tot)
    for pair in pairs:
        Ct_tot_from_partials += getattr(sample2, f'Ctqt_{pair}')
    assert np.allclose(Ct_tot, Ct_tot_from_partials)

    # test self-parts
    Fs_tot1 = sample1.Fqt_incoh_X
    Fs_tot2 = sample2.Fqt_incoh
    assert np.allclose(Fs_tot1, Fs_tot2)

    Fs_tot_from_partials = np.zeros_like(Fs_tot1)
    atom_types = ['Cs', 'Br', 'Pb']
    for atom_type in atom_types:
        Fs_tot_from_partials += getattr(sample2, f'Fqt_incoh_{atom_type}')
    assert np.allclose(Fs_tot1, Fs_tot_from_partials)


def test_normalization_static_structure_factor():

    # traj index files
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(
        this_dir, 'trajectory_reader/trajectory_files/dump_long_with_velocities.xyz')
    index_fname = os.path.join(this_dir, 'trajectory_reader/trajectory_files/index_file_dump_long')

    # input parameters
    q_max = 40
    max_points = 500

    # setup
    traj_format = 'extxyz'
    traj = Trajectory(traj_fname, trajectory_format=traj_format)
    q_points = get_spherical_qpoints(traj.cell, q_max=q_max, max_points=max_points)

    # run only total
    sample1 = compute_static_structure_factors(traj, q_points)
    record = sample1.history[0]
    assert record['func'] == 'compute_static_structure_factors'
    assert 'date_time' in record

    # run with partial
    traj = Trajectory(traj_fname, trajectory_format=traj_format, atomic_indices=index_fname)
    sample2 = compute_static_structure_factors(traj, q_points)

    # test S(q)
    F_tot = sample1.Sq_X_X
    pairs = ['Cs_Cs', 'Br_Br', 'Pb_Pb', 'Cs_Pb', 'Br_Cs', 'Br_Pb']
    F_tot_from_partials = np.zeros_like(F_tot)
    for pair in pairs:
        F_tot_from_partials += getattr(sample2, f'Sq_{pair}')
    assert np.allclose(F_tot, F_tot_from_partials)
