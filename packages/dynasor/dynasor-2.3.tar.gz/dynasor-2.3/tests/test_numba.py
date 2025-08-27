import pytest
import numpy as np

from dynasor.core.reciprocal import calc_rho_q, calc_rho_j_q


# Setup test arrays and inputs

@pytest.fixture
def xvq():
    Nx = 4
    Nq = 5
    np.random.seed(42)
    x = np.random.normal(size=(Nx, 3))
    v = np.random.normal(size=(Nx, 3))
    q = np.random.normal(size=(Nq, 3))
    return x, v, q


def test_rho_j_q(xvq):
    x, v, q = xvq
    rho_q, rho_j_q = calc_rho_j_q(x, v, q)
    rho_q2 = calc_rho_q(x, q)
    assert np.allclose(rho_q, rho_q2)
    Nx = x.shape[0]

    rho_q_target = Nx**0.5 * np.array([1.6509947-0.7272682j,
                                       1.74291595+0.81511274j,
                                       1.16879217-0.98689153j,
                                       1.00661299-1.40743052j,
                                       1.06588947+0.44672131j])
    rho_j_q_target = Nx**0.5 * np.array(
        [[-0.72463296+0.13571632j, -1.56724203+1.27085398j, -0.29899287+0.34897803j],
         [-0.60871115-0.37439687j, -1.96631866-0.60202257j, -0.62226018-0.17672867j],
         [-0.40649785+0.10510835j, -1.53524612+0.6491588j,  -0.31563418+1.30276366j],
         [-0.50810342+0.40748936j, -0.76088817+1.75737831j, -0.11795971+0.63627665j],
         [-0.4026586-0.18057006j, -1.68535262+0.40104027j, -0.01598231-0.55236761j]])

    assert np.allclose(rho_q, rho_q_target)
    assert np.allclose(rho_j_q, rho_j_q_target)
