import pytest
import numpy as np
from dynasor.post_processing.spherical_average import _get_bin_average, _gaussian
from dynasor.post_processing import get_spherically_averaged_sample_smearing
from dynasor.post_processing import get_spherically_averaged_sample_binned
from dynasor.sample import DynamicSample, StaticSample


def test_spherical_averaging():
    N_q = 100
    N_t = 8
    qbins = 20

    np.random.seed(42)
    data = np.random.random((N_q, N_t))
    q_points = np.random.random((N_q, 3))

    q_bincenters, bin_counts, averaged_data = _get_bin_average(q_points, data, qbins)
    assert len(q_bincenters) == qbins
    assert averaged_data.shape == (qbins, N_t)

    # check q_bincenters
    q_min = np.min(np.linalg.norm(q_points, axis=1))
    q_max = np.max(np.linalg.norm(q_points, axis=1))
    assert np.isclose(q_bincenters[0], q_min)
    assert np.isclose(q_bincenters[-1], q_max)

    # check bin counts
    bin_counts_target = np.array([2, 2, 3, 1, 4, 0, 5, 10, 9, 16, 7, 11, 5, 6, 8, 4, 5, 0, 1, 1])
    assert np.allclose(bin_counts, bin_counts_target)

    # check for Nans for empty bins
    for bin_index in np.where(bin_counts == 0)[0]:
        assert np.all(np.isnan(averaged_data[bin_index]))

    # check averaged data
    target_average = np.array([0.59242063, 0.44607297, 0.45898736, 0.64679424, 0.66729803,
                               0.45030113, 0.417301, 0.59437702])
    assert np.allclose(averaged_data[10], target_average)


def test_spherical_summing_vs_averaging():
    q_min = 0.0
    q_max = 10.0
    n_bins = 100

    # make some dummy q-points with more q-ponts at some places
    q_bins = np.linspace(q_min, q_max, n_bins).tolist()
    q_bins += [1.0, 1.0, 1.0, 1.0]
    q_points = np.append(np.array(sorted(q_bins)),
                         np.zeros(2*len(q_bins))).reshape(3, len(q_bins)).T

    # add two peaks
    Sq_raw = np.zeros(len(q_bins))
    Sq_raw[10] = 1.0
    Sq_raw[54] = 1.0

    q_bincenters_sum, bin_counts_sum, summed_data = _get_bin_average(q_points,
                                                                     Sq_raw.reshape(-1, 1),
                                                                     n_bins, use_sum=True)

    q_bincenters_avg, bin_counts_avg, averaged_data = _get_bin_average(q_points,
                                                                       Sq_raw.reshape(-1, 1),
                                                                       n_bins, use_sum=False)

    assert len(q_bincenters_sum) == len(q_bincenters_avg)
    assert summed_data[10] == summed_data[50]
    assert averaged_data[10] < averaged_data[50]
    assert averaged_data[10] < summed_data[10]


def test_spherical_averaging_of_dynamic_sample(dynamic_sample_with_incoh):
    # binning average
    q_bins = 14
    sample_res = get_spherically_averaged_sample_binned(dynamic_sample_with_incoh, q_bins)
    assert isinstance(sample_res, DynamicSample)
    for key in sample_res.available_correlation_functions:
        assert sample_res[key].shape == (q_bins, dynamic_sample_with_incoh[key].shape[1])

    # gaussian average
    q_norms = np.linspace(0, 1.5, 100)
    q_width = 0.1
    sample_res = get_spherically_averaged_sample_smearing(
        dynamic_sample_with_incoh, q_norms=q_norms, q_width=q_width)
    assert isinstance(sample_res, DynamicSample)
    for key in sample_res.available_correlation_functions:
        assert sample_res[key].shape == (len(q_norms), dynamic_sample_with_incoh[key].shape[1])


def test_spherical_averaging_of_samples(static_sample):
    # binning
    q_bins = 14
    sample_res = get_spherically_averaged_sample_binned(static_sample, q_bins)
    assert isinstance(sample_res, StaticSample)
    for key in sample_res.available_correlation_functions:
        assert sample_res[key].shape == (q_bins, static_sample[key].shape[1])

    # gaussian
    q_norms = np.linspace(0, 1.5, 100)
    q_width = 0.1
    sample_res = get_spherically_averaged_sample_smearing(
        static_sample, q_norms=q_norms, q_width=q_width)
    assert isinstance(sample_res, StaticSample)
    for key in sample_res.available_correlation_functions:
        assert sample_res[key].shape == (len(q_norms), static_sample[key].shape[1])


def test_raises_error_with_invalid_inputs(dynamic_sample_with_incoh):

    q_bins = 14
    q_norms = np.linspace(0, 1.5, 100)
    q_width = 0.1

    # invalid sample
    bad_sample = np.random.random((10, 20, 3))
    with pytest.raises(ValueError):
        get_spherically_averaged_sample_binned(bad_sample, q_bins)
    with pytest.raises(ValueError):
        get_spherically_averaged_sample_smearing(bad_sample, q_norms=q_norms, q_width=q_width)

    # invalid q-points shape
    qpts = dynamic_sample_with_incoh.q_points
    dynamic_sample_with_incoh.q_points = np.hstack((qpts, np.ones((qpts.shape[0], 1))))
    with pytest.raises(ValueError):
        get_spherically_averaged_sample_binned(dynamic_sample_with_incoh, q_bins)
    with pytest.raises(ValueError):
        get_spherically_averaged_sample_smearing(
            dynamic_sample_with_incoh, q_norms=q_norms, q_width=q_width)


def test_gaussian():
    x = np.array([1.0, 2.0, 0.0, 2.23])
    x0 = 1.0
    sigma = 1.2

    f = _gaussian(x, x0, sigma)
    f_target = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-1/2 * (x-x0)**2 / sigma**2)

    assert np.allclose(f, f_target)
