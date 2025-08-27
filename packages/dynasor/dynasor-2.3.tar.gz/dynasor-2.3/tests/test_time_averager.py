import numpy as np
from dynasor.core.time_averager import TimeAverager


np.random.seed(42)


def test_time_averager():
    window = 11
    array_size = 20

    averager = TimeAverager(window, array_size)

    # add a single sample
    sample1 = np.random.random((array_size, ))
    averager.add_sample(time_lag=0, sample=sample1)
    average_array = averager.get_average_all()

    assert average_array.shape == (array_size, window)
    assert np.allclose(sample1, average_array[:, 0])
    for t in range(1, window):
        assert np.all(np.isnan(average_array[:, t]))

    # add additional sample
    sample2 = np.random.random((array_size, ))
    sample3 = np.random.random((array_size, ))

    averager.add_sample(time_lag=0, sample=sample2)
    averager.add_sample(time_lag=5, sample=sample3)
    average_array = averager.get_average_all()

    assert np.allclose(average_array[:, 0], (sample1+sample2) / 2.0)
    assert np.allclose(average_array[:, 5], sample3)
