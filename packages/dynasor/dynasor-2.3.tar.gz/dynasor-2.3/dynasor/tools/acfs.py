"""
A number of utility functions, for example for dealing with
autocorrelation functions, Fourier transforms, and smoothing.
"""

from typing import Optional
import numpy as np
from scipy.signal import correlate
from numpy.typing import NDArray
import pandas as pd


def psd_from_acf(
    acf: NDArray[float],
    dt: Optional[float] = 1,
    angular: Optional[bool] = True,
    even: Optional[bool] = True,
) -> NDArray[float]:
    """Computes the power spectral density (PSD) from an auto-correlation function (ACF).

    Parameters
    ----------
    acf
        The ACF as an array.
    dt
        The time step between samples.
    angular
        Whether to return normal or angular frequencies.
    even
        Whether to mirror the ACF and force the PSD to be purely real.
    """
    assert acf.ndim == 1
    signal = np.array(acf)
    if even:
        signal = np.hstack((signal, signal[:0:-1]))
    fft = np.fft.fft(signal)
    if even:
        assert np.allclose(fft.imag, 0)
    fft = fft.real if even else fft

    freqs = np.fft.fftfreq(len(signal), dt)
    freqs = 2*np.pi * freqs if angular else freqs

    return freqs, fft


def compute_acf(
    Z: NDArray[float],
    delta_t: Optional[float] = 1.0,
    method: Optional[str] = 'scipy',
) -> NDArray[float]:
    r"""
    Computes the autocorrelation function (ACF) for a one-dimensional signal :math:`Z` in time as

    .. math::

        \text{ACF}(\tau) = \frac{\left < Z(t) Z^*(t+\tau) \right >}{\left <  Z(t)  Z^*(t) \right >}

    Here, only the real part of the ACF is returned since if :math:`Z` is complex
    the imaginary part should average out to zero for any stationary signal.

    Parameters
    ----------
    Z
        Complex time signal.
    delta_t
        Spacing in time between two consecutive values in :math:`Z`.
    method
        Implementation to use; possible values: `numpy` and `scipy` (default and usually faster).
    """

    # keep only real part and normalize
    acf = _compute_correlation_function(Z, Z, method)
    acf = np.real(acf)
    acf /= acf[0]

    time_lags = delta_t * np.arange(0, len(acf), 1)
    return time_lags, acf


def _compute_correlation_function(Z1, Z2, method: Optional[str] = 'scipy'):
    N = len(Z1)
    assert len(Z1) == len(Z2)
    if method == 'scipy':
        cf = correlate(Z1, Z2, mode='full')[N - 1:] / np.arange(N, 0, -1)
    elif method == 'numpy':
        cf = np.correlate(Z1, Z2, mode='full')[N - 1:] / np.arange(N, 0, -1)
    else:
        raise ValueError('method must be either numpy or scipy')
    return cf


# smoothing functions / FFT filters
# -------------------------------------
def gaussian_decay(t: NDArray[float], t_sigma: float) -> NDArray[float]:
    r"""
    Evaluates a gaussian distribution in time :math:`f(t)`, which can be applied to an ACF in time
    to artificially damp it, i.e., forcing it to go to zero for long times.

    .. math::

        f(t) = \exp{\left [-\frac{1}{2} \left (\frac{t}{t_\mathrm{sigma}}\right )^2 \right ] }

    Parameters
    ----------
    t
        Time array.
    t_sigma
        Width (standard deviation of the gaussian) of the decay.
    """

    return np.exp(- 1 / 2 * (t / t_sigma) ** 2)


def fermi_dirac(t: NDArray[float], t_0: float, t_width: float) -> NDArray[float]:
    r"""
    Evaluates a Fermi-Dirac-like function in time :math:`f(t)`, which can be applied to an
    auto-correlation function (ACF) in time to artificially dampen it, i.e., forcing it to
    go to zero for long times without affecting the short-time correlations too much.

    .. math::

        f(t) = \frac{1}{\exp{[(t-t_0)/t_\mathrm{width}}] + 1}

    Parameters
    ----------
    t
        Time array.
    t_0
        Starting time for decay.
    t_width
        Width of the decay.

    """
    return 1.0 / (np.exp((t - t_0) / t_width) + 1)


def smoothing_function(
    data: NDArray[float],
    window_size: int,
    window_type: Optional[str] = 'hamming',
) -> NDArray[float]:
    """
    Smoothing function for 1D arrays.
    This functions employs the pandas rolling window average function.

    Parameters
    ----------
    data
        1D data array.
    window_size
        The size of smoothing/smearing window.
    window_type
        What type of window-shape to use, e.g. ``'blackman'``, ``'hamming'``, ``'boxcar'``
        (see pandas and scipy documentaiton for more details).

    """
    series = pd.Series(data)
    new_data = series.rolling(window_size, win_type=window_type, center=True, min_periods=1).mean()
    return np.array(new_data)
