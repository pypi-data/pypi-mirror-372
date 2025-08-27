import os
import numpy as np
import pytest
from dynasor.trajectory import Trajectory
from dynasor.qpoints import get_spherical_qpoints
from dynasor.correlation_functions import compute_static_structure_factors
from dynasor.correlation_functions import compute_dynamic_structure_factors
from dynasor.post_processing import get_spherically_averaged_sample_binned
from dynasor.post_processing import Weights, get_weighted_sample


@pytest.fixture
def traj_fname():
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(
        this_dir, 'trajectory_reader/trajectory_files/dump_long_with_velocities.xyz')
    return traj_fname


def test_integration_static_structure_factor(traj_fname):
    """ Test the full dynasor workflow for static structure factor """

    # parameters
    q_max = 1.9
    max_points = 600
    q_bins = 17

    # run dynasor
    traj = Trajectory(traj_fname, trajectory_format='extxyz', atomic_indices='read_from_trajectory')
    q_points = get_spherical_qpoints(traj.cell, q_max=q_max, max_points=max_points)
    sample = compute_static_structure_factors(traj, q_points)

    # check that sample contains metadata
    assert sample.simulation_data['number_of_frames'] == 30

    # post process
    sample_averaged = get_spherically_averaged_sample_binned(sample, num_q_bins=q_bins)
    assert sample_averaged.pairs is not None
    weights_dict = dict(Cs=2.05, Pb=0.55, Br=0.33)
    weights = Weights(weights_dict)
    sample_weighted = get_weighted_sample(sample_averaged, weights)

    # check outputs
    assert sample_weighted.dimensions == ['q_norms']
    assert sample_weighted.q_norms.shape == (17, )

    expected_names = ['Sq', 'Sq_Cs_Cs', 'Sq_Cs_Pb', 'Sq_Br_Cs', 'Sq_Pb_Pb', 'Sq_Br_Pb', 'Sq_Br_Br']
    assert sorted(sample_weighted.available_correlation_functions) == sorted(expected_names)
    for name in expected_names:
        assert sample_weighted[name].shape == (q_bins, 1)

    assert sample_weighted.atom_types == ['Br', 'Cs', 'Pb']
    assert sample_weighted.pairs == [('Br', 'Br'), ('Br', 'Cs'), ('Br', 'Pb'), ('Cs', 'Cs'),
                                     ('Cs', 'Pb'), ('Pb', 'Pb')]
    assert np.allclose(sample_weighted.cell, 23.77195271 * np.eye(3))
    assert sample_weighted.particle_counts == dict(Br=192, Cs=64, Pb=64)

    # regression test vs old results
    Sq_Br_Cs_target = [[5.19552000e+01],
                       [np.nan],
                       [6.84210294e-04],
                       [9.95972202e-04],
                       [-3.94002366e-04],
                       [6.41177648e-04],
                       [-3.16270130e-03],
                       [-6.22960908e-03],
                       [-1.33103518e-04],
                       [-1.19255936e+00],
                       [-1.50112979e-02],
                       [-3.08410954e-02],
                       [-1.21697876e-02],
                       [-1.00354901e+00],
                       [1.95727845e-02],
                       [4.71059534e-03],
                       [3.59197778e+00]]

    result = list(sample_weighted.Sq_Br_Cs)
    assert np.allclose(result, Sq_Br_Cs_target, equal_nan=True)


def test_integration_dynamic_structure_factor(traj_fname):
    """ Test the full dynasor workflow for dynamic structure factor """

    # parameters
    q_max = 2.5
    max_points = 35
    q_bins = 6
    window_size = 4
    dt = 2.1

    # run dynasor
    traj = Trajectory(traj_fname, trajectory_format='extxyz', atomic_indices='read_from_trajectory')
    q_points = get_spherical_qpoints(traj.cell, q_max=q_max, max_points=max_points)
    sample = compute_dynamic_structure_factors(traj, q_points, dt=dt, window_size=window_size,
                                               calculate_incoherent=True, calculate_currents=True)

    # check that sample contains metadata
    assert sample.simulation_data['number_of_frames'] == 30
    assert sample.simulation_data['time_between_frames'] == dt
    assert sample.simulation_data['maximum_time_lag'] == window_size * dt
    assert sample.simulation_data['angular_frequency_resolution'] \
        == 2 * np.pi / (window_size * 2 * dt)
    assert sample.simulation_data['maximum_angular_frequency'] == 2 * np.pi / (2 * dt)
    assert np.allclose(sample.time, dt * np.linspace(0, window_size, window_size + 1))

    # post process
    sample_averaged = get_spherically_averaged_sample_binned(sample, num_q_bins=q_bins)
    assert sample_averaged.pairs is not None
    weights_coh = dict(Cs=2.05, Pb=0.55, Br=0.33)
    weights_incoh = dict(Cs=2.05, Pb=0.55, Br=0.33)
    weights = Weights(weights_coh, weights_incoh)
    sample_weighted = get_weighted_sample(sample_averaged, weights)

    # check outputs
    assert sample_weighted.dimensions == ['omega', 'q_norms', 'time']
    assert sample_weighted.omega.shape == (window_size + 1, )
    assert sample_weighted.time.shape == (window_size + 1, )
    assert sample_weighted.q_norms.shape == (q_bins, )

    expected_atom_types = ['Br', 'Cs', 'Pb']
    expected_pairs = [('Br', 'Br'), ('Br', 'Cs'), ('Br', 'Pb'), ('Cs', 'Cs'),
                      ('Cs', 'Pb'), ('Pb', 'Pb')]
    expected_correlations = []
    for name in ['Fqt_coh', 'Sqw_coh', 'Clqt', 'Clqw', 'Ctqt', 'Ctqw']:
        expected_correlations.append(name)
        for s1, s2 in expected_pairs:
            expected_correlations.append(f'{name}_{s1}_{s2}')
    for name in ['Fqt_incoh', 'Sqw_incoh']:
        expected_correlations.append(name)
        for atom_type in expected_atom_types:
            expected_correlations.append(f'{name}_{atom_type}')

    assert sorted(sample_weighted.available_correlation_functions) == sorted(expected_correlations)
    for name in expected_correlations:
        if 'qw' in name:
            assert sample_weighted[name].shape == (q_bins, window_size + 1)
        else:
            assert sample_weighted[name].shape == (q_bins, window_size + 1)

    assert sample_weighted.atom_types == expected_atom_types
    assert sample_weighted.pairs == expected_pairs
    assert np.allclose(sample_weighted.cell, 23.77195271 * np.eye(3))
    assert sample_weighted.particle_counts == dict(Br=192, Cs=64, Pb=64)
