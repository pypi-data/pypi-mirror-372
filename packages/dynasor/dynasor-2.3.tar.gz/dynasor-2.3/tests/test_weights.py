import pytest
import numpy as np
from dynasor.post_processing import Weights


@pytest.fixture
def weights_coh():
    weights_coh = dict()
    weights_coh['A'] = 1.40
    weights_coh['B'] = 0.98
    weights_coh['some-group'] = 12.99
    return weights_coh


@pytest.fixture
def weights_incoh():
    weights_incoh = dict()
    weights_incoh['B'] = 11.0
    weights_incoh['some-group'] = 45.8
    weights_incoh['A'] = 23.2
    return weights_incoh


def test_init_weights(weights_coh, weights_incoh):

    # without incoherent
    weights = Weights(weights_coh)
    assert weights.supports_currents
    assert not weights.supports_incoherent

    # with incoherent
    weights = Weights(weights_coh, weights_incoh)
    assert weights.supports_currents
    assert weights.supports_incoherent

    # without currents
    weights = Weights(weights_coh, weights_incoh, supports_currents=False)
    assert not weights.supports_currents
    assert weights.supports_incoherent


def test_get_weights(weights_coh, weights_incoh):

    weights = Weights(weights_coh, weights_incoh)
    assert weights.supports_currents
    assert weights.supports_incoherent

    # check coherent weights
    for key, val in weights_coh.items():
        assert np.isclose(val, weights.get_weight_coh(key))

    # check incoherent weights
    for key, val in weights_incoh.items():
        assert np.isclose(val, weights.get_weight_incoh(key))


def test_weights_parameters(weights_coh, weights_incoh):

    # without incoherent
    weights = Weights(weights_coh)
    pars = weights.parameters
    assert 'coherent' in pars.columns
    assert 'incoherent' not in pars.columns

    # with incoherent
    weights = Weights(weights_coh, weights_incoh)
    pars = weights.parameters
    assert 'coherent' in pars.columns
    assert 'incoherent' in pars.columns

    for s in weights_coh:
        assert pars[pars.atom_type == s]['coherent'].iloc[0] == weights_coh[s]
    for s in weights_incoh:
        assert pars[pars.atom_type == s]['incoherent'].iloc[0] == weights_incoh[s]
