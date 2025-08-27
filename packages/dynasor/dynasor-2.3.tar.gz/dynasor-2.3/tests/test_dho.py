import numpy as np
import pytest
from dynasor.tools.damped_harmonic_oscillator import acf_position_dho, acf_velocity_dho
from dynasor.tools.damped_harmonic_oscillator import psd_position_dho, psd_velocity_dho


# parameters
dt = 0.5
N = 200

w0 = 2.0
gamma = 0.5
A = 1.5
tau = 2 / gamma


@pytest.fixture
def time():
    return np.arange(0, N*dt, dt)


@pytest.fixture
def omega():
    return np.linspace(0.0, 2 * np.pi / dt, N)


def test_acf_position_dho(time):

    # check t=0 value
    acf = acf_position_dho(t=0.0, w0=w0, gamma=gamma, A=A)
    assert np.isclose(acf, A)

    # check that acf decay to zero after
    acf = acf_position_dho(t=15 * tau, w0=w0, gamma=gamma, A=A)
    assert abs(acf) < 1e-6

    # check with time array
    for sign in [-1, 1]:
        acf = acf_position_dho(t=sign * time, w0=w0, gamma=gamma, A=A)
        assert len(acf) == len(time)
        acf_target_t10 = np.array([1.5, 0.86356344, -0.33464699, -0.99556173, -0.70034213,
                                   0.09933936, 0.64131426, 0.54166271, 0.02338361, -0.39927632])
        assert np.allclose(acf[0:10], acf_target_t10)

    # check that it works without errors in various limits
    gamma_values = [1.0, np.sqrt(2.0), 2.0, 4.0, 20.0]
    for g in gamma_values:
        acf = acf_position_dho(t=time, w0=w0, gamma=g*w0, A=A)
        assert len(acf) == len(time)


def test_acf_velocity_dho(time):

    # check t=0 value
    acf = acf_velocity_dho(t=0.0, w0=w0, gamma=gamma, A=A)
    assert np.isclose(acf, A * w0**2)

    # check that acf decay to zero after
    acf = acf_velocity_dho(t=15 * tau, w0=w0, gamma=gamma, A=A)
    assert abs(acf) < 1e-5

    # check with time array
    acf = acf_velocity_dho(t=time, w0=w0, gamma=gamma, A=A)
    assert len(acf) == len(time)

    # check with time array
    for sign in [-1, 1]:
        acf = acf_velocity_dho(t=sign * time, w0=w0, gamma=gamma, A=A)
        assert len(acf) == len(time)
        acf_target_t10 = np.array([6.0, 2.33724331, -2.41678174, -4.15304431, -2.12653247,
                                   1.18175974, 2.79683816, 1.77929125, -0.46071975, -1.83042293])
        assert np.allclose(acf[0:10], acf_target_t10)

    # check that it works without errors in various limits
    gamma_values = [1.0, np.sqrt(2.0), 2.0, 4.0, 20.0]
    for g in gamma_values:
        acf = acf_velocity_dho(t=time, w0=w0, gamma=g*w0, A=A)
        assert len(acf) == len(time)


def test_psd_position_dho(omega):

    # check omega=0 value
    psd = psd_position_dho(w=0.0, w0=w0, gamma=gamma, A=A)
    assert np.isclose(psd, A * 2 * gamma / w0**2)

    # check with omega array
    psd = psd_position_dho(w=omega, w0=w0, gamma=gamma, A=A)
    assert len(psd) == len(omega)
    psd_target_t10 = np.array([0.375, 0.37572534, 0.37791376, 0.38160288, 0.38685702, 0.39376959,
                              0.40246679, 0.41311274, 0.42591638, 0.4411408])
    assert np.allclose(psd[0:10], psd_target_t10)


def test_psd_velocity_dho(omega):
    psd_r = psd_position_dho(omega, w0, gamma, A)
    psd_v = psd_velocity_dho(omega, w0, gamma, A)
    assert np.allclose(omega ** 2 * psd_r, psd_v)
