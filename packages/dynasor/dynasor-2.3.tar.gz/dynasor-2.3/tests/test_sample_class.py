from tempfile import NamedTemporaryFile

import numpy as np
import pytest

from dynasor.sample import Sample, DynamicSample, StaticSample, read_sample_from_npz

N_qpoints = 20
window_size = 100


@pytest.fixture
def q_points():
    return np.array([np.array([1, 0, 0]) * amp for amp in np.linspace(0, 1, N_qpoints)])


@pytest.fixture
def time():
    return np.linspace(0, 10, window_size)


@pytest.fixture
def omega():
    return np.linspace(0, 5, window_size)


@pytest.fixture
def data_dict(q_points, time, omega):
    # setup data dict
    data_dict = dict()
    data_dict['q_points'] = q_points
    data_dict['time'] = time
    data_dict['omega'] = omega

    shape = (N_qpoints, window_size)
    data_dict['Fqt_coh_A_A'] = np.linspace(-1, 1, N_qpoints * window_size).reshape(shape)
    data_dict['Fqt_coh_B_B'] = np.linspace(-0.4, 0.4, N_qpoints * window_size).reshape(shape)
    data_dict['Fqt_coh_A_B'] = np.linspace(-0.3, 0.3, N_qpoints * window_size).reshape(shape)
    data_dict['Fqt_coh'] = data_dict['Fqt_coh_A_A'] + data_dict['Fqt_coh_A_B'] + \
        data_dict['Fqt_coh_B_B']
    data_dict['Sqw_coh_A_A'] = np.linspace(-10, 10, N_qpoints * window_size).reshape(shape)
    data_dict['Sqw_coh_B_B'] = np.linspace(-4, 4, N_qpoints * window_size).reshape(shape)
    data_dict['Sqw_coh_A_B'] = np.linspace(-3, 3, N_qpoints * window_size).reshape(shape)
    data_dict['Sqw_coh'] = data_dict['Sqw_coh_A_A'] + data_dict['Sqw_coh_A_B'] + \
        data_dict['Sqw_coh_B_B']

    return data_dict


@pytest.fixture
def data_dict_static(q_points):
    data_dict = dict()
    data_dict['q_points'] = q_points
    size = (q_points.shape[0], 1)
    data_dict['Sq_A_A'] = np.random.random(size)
    data_dict['Sq_A_B'] = np.random.random(size)
    data_dict['Sq_B_B'] = np.random.random(size)
    data_dict['Sq'] = np.random.random(size)
    return data_dict


@pytest.fixture
def simulation_data():
    atom_types = ['A', 'B']
    pairs = [('A', 'A'), ('A', 'B'), ('B', 'B')]
    counts = dict(A=500, B=250)
    cell = np.diag([2.5, 3.8, 2.95])
    simulation_data = dict(atom_types=atom_types, pairs=pairs, particle_counts=counts, cell=cell)
    return simulation_data


@pytest.fixture
def simple_sample(data_dict, simulation_data):
    sample = Sample(data_dict, simulation_data)
    return sample


def test_getattributes(q_points, time, simple_sample):
    assert np.allclose(simple_sample.q_points, q_points)
    assert np.allclose(simple_sample.time, time)


def test_getitem(data_dict, simple_sample):
    for key in data_dict:
        assert np.allclose(data_dict[key], getattr(simple_sample, key))

    # check that sample.xyz and sample['xyz'] return the same thing for an item in data_dict and
    # one in simulation_data
    assert np.allclose(simple_sample.cell, simple_sample['cell'])
    assert np.allclose(simple_sample.Sqw_coh_B_B, simple_sample['Sqw_coh_B_B'])


def test_repr_str(simple_sample):
    s1 = repr(simple_sample)
    s2 = str(simple_sample)
    assert isinstance(s1, str)
    assert s1 == s2


def test_repr_html_str(simple_sample):
    s = simple_sample._repr_html_()
    assert isinstance(s, str)


def test_read_and_write(data_dict, simulation_data, simple_sample):

    # write to file
    tempfile = NamedTemporaryFile(suffix='.npz', delete=False)
    simple_sample.write_to_npz(tempfile.name)
    for key, val in data_dict.items():
        assert np.allclose(data_dict[key], getattr(simple_sample, key))

    # read from file
    new_sample = read_sample_from_npz(tempfile.name)

    # check that nothing changed with metadata
    assert sorted(simple_sample.simulation_data.keys()) == sorted(new_sample.simulation_data.keys())

    assert simulation_data['atom_types'] == new_sample.atom_types
    assert simulation_data['pairs'] == new_sample.pairs
    assert np.allclose(simulation_data['cell'], new_sample.cell)
    for key in simulation_data['particle_counts']:
        assert simulation_data['particle_counts'][key] == new_sample.particle_counts[key]
    # check that nothing changed with correlation function data
    for key, val in data_dict.items():
        assert np.allclose(data_dict[key], getattr(new_sample, key))


def test_static_sample(data_dict_static, simulation_data):
    sample = StaticSample(data_dict_static, simulation_data)
    assert len(sample.available_correlation_functions) == 4
    for key in sample.available_correlation_functions:
        assert np.allclose(sample[key], data_dict_static[key])


def test_dynamic_sample(data_dict, simulation_data):
    sample = DynamicSample(data_dict, simulation_data)
    assert len(sample.available_correlation_functions) == 8
    for key in sample.available_correlation_functions:
        assert np.allclose(sample[key], data_dict[key])


def test_dynamic_sample_properties(data_dict, simulation_data):
    # without incoherent, without currents
    sample = DynamicSample(data_dict, simulation_data)
    assert not sample.has_currents
    assert not sample.has_incoherent

    # with incoherent, without currents
    data_dict['Fqt_incoh'] = np.zeros(sample.Fqt_coh.shape)
    sample = DynamicSample(data_dict, simulation_data)
    assert not sample.has_currents
    assert sample.has_incoherent
    assert sorted(sample.dimensions) == sorted(['omega', 'q_points', 'time'])
    for key, val in simulation_data.items():
        assert key in sample.simulation_data
        if isinstance(val, dict) or isinstance(val, list):
            assert val == sample.simulation_data[key]
        else:
            assert np.allclose(val, sample.simulation_data[key])
    assert 'history' in sample.metadata
    assert isinstance(sample.history, list)

    # with incoherent and currents
    data_dict['Clqt_A_A'] = np.zeros(sample.Fqt_coh.shape)
    data_dict['Clqt_A_B'] = np.zeros(sample.Fqt_coh.shape)
    data_dict['Clqt_B_B'] = np.zeros(sample.Fqt_coh.shape)
    sample = DynamicSample(data_dict, simulation_data)
    assert sample.has_currents
    assert sample.has_incoherent
    assert sorted(sample.dimensions) == sorted(['omega', 'q_points', 'time'])


def test_static_sample_properties(data_dict_static, simulation_data):
    sample = StaticSample(data_dict_static, simulation_data)
    assert not sample.has_currents
    assert not sample.has_incoherent
    assert sample.dimensions == ['q_points']


def test_dynamic_to_dataframe(data_dict, simulation_data):
    # without incoherent, without currents
    sample = DynamicSample(data_dict, simulation_data)
    q_index = 5
    df = sample.to_dataframe(q_index=q_index)

    for key in ['time', 'omega']:
        assert np.allclose(df[key], sample[key])

    for key in sample.available_correlation_functions:
        assert np.allclose(df[key], sample[key][q_index])


def test_static_to_dataframe(data_dict_static, simulation_data):
    sample = StaticSample(data_dict_static, simulation_data)
    df = sample.to_dataframe()
    for key in sample.available_correlation_functions:
        assert np.allclose(df[key], sample[key].reshape(-1, ))
