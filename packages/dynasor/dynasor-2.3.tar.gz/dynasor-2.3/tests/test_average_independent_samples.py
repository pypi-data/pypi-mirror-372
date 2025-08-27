import numpy as np
import pytest
from dynasor.sample import DynamicSample
from dynasor.post_processing import get_sample_averaged_over_independent_runs


dynamic_correlation_functions = ['Fqt', 'Fqt_coh', 'Fqt_coh_A_A', 'Fqt_coh_A_B', 'Fqt_coh_B_B',
                                 'Fqt_incoh', 'Fqt_incoh_A', 'Fqt_incoh_B',
                                 'Sqw', 'Sqw_coh', 'Sqw_coh_A_A', 'Sqw_coh_A_B', 'Sqw_coh_B_B',
                                 'Sqw_incoh', 'Sqw_incoh_A', 'Sqw_incoh_B']


def get_random_dynamic_data_dict(n_q, n_t):
    """ generate a random data_dict """
    data_dict = dict()
    data_dict['q_points'] = np.linspace([0, 0, 0], [1.0, 1.0, 1.5], n_q)
    data_dict['time'] = np.linspace(0, 10, n_t)
    data_dict['omega'] = np.linspace(0, 3, n_t)

    for name in dynamic_correlation_functions:
        data_dict[name] = np.random.normal(0, 10, (n_q, n_t))
    return data_dict


def get_random_dynamic_sample():
    n_q = 50
    n_t = 200
    data_dict = get_random_dynamic_data_dict(n_q, n_t)
    sample = DynamicSample(data_dict, simulation_data=get_simulation_data())
    return sample


def get_simulation_data():
    simulation_data = dict()
    simulation_data['cell'] = np.diag([11.5, 18.2, 10.1])
    simulation_data['atom_types'] = ['A', 'B']
    simulation_data['particle_counts'] = dict(A=100, B=250)
    simulation_data['pairs'] = [('A', 'A'), ('A', 'B'), ('B', 'B')]
    return simulation_data


def test_average_dynamic_samples():

    # setup samples to average over
    n_samples = 25
    simulation_data_ref = get_simulation_data()
    samples = [get_random_dynamic_sample() for _ in range(n_samples)]

    # average
    sample_ave = get_sample_averaged_over_independent_runs(samples)
    assert isinstance(sample_ave, DynamicSample)

    # check dimensions are correct
    assert sorted(sample_ave.dimensions) == ['omega', 'q_points', 'time']
    assert np.allclose(sample_ave.omega, samples[0].omega)
    assert np.allclose(sample_ave.q_points, samples[0].q_points)
    assert np.allclose(sample_ave.time, samples[0].time)

    # check metadata is correct
    assert 'simulation_data' in sample_ave.metadata
    assert 'history' in sample_ave.metadata
    assert np.allclose(sample_ave.cell, simulation_data_ref['cell'])
    assert sample_ave.particle_counts == simulation_data_ref['particle_counts']
    assert sample_ave.atom_types, simulation_data_ref['atom_types']
    assert sample_ave.pairs, simulation_data_ref['pairs']

    # check value of correlation functions is correct
    for name in dynamic_correlation_functions:
        average = np.mean([sample[name] for sample in samples], axis=0)
        assert np.allclose(average, sample_ave[name])


def test_raises_error_with_inconsistent_samples():

    n_samples = 25

    # inconsistent metadata
    samples = [get_random_dynamic_sample() for _ in range(n_samples)]
    samples[10]._metadata['simulation_data']['cell'] = 4.19 * np.eye(3)
    with pytest.raises(ValueError) as e:
        get_sample_averaged_over_independent_runs(samples)
    assert 'Field "cell" of sample #10 does not match.' in str(e)

    # inconsistent dimensions
    samples = [get_random_dynamic_sample() for _ in range(n_samples)]
    samples[4].q_points[0, 0] = 0.212354
    with pytest.raises(ValueError) as e:
        get_sample_averaged_over_independent_runs(samples)
    assert 'Sample dimensions do not match for sample #4.' in str(e)
