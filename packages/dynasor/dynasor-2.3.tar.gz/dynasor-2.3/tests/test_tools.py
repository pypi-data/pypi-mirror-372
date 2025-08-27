import numpy as np
import pytest
from ase.build import bulk
from dynasor.tools.acfs import compute_acf, fermi_dirac, smoothing_function
from dynasor.tools.structures import align_structure
from dynasor.tools.structures import get_offset_index


@pytest.fixture
def signal_complex():
    np.random.seed(42)
    N = 1000
    x = np.random.random((N, ))
    y = np.random.random((N, ))
    Z_t = x + 1j * y
    return Z_t


def test_numpy_scipy_acf(signal_complex):
    delta_t = 0.25
    t1, acf1 = compute_acf(signal_complex, delta_t=delta_t, method='numpy')
    t2, acf2 = compute_acf(signal_complex, delta_t=delta_t, method='scipy')
    assert np.allclose(t1, t2)
    assert np.allclose(acf1, acf2)


def test_compute_acf_invalid_arguments(signal_complex):
    with pytest.raises(ValueError):
        t1, acf1 = compute_acf(signal_complex, method='asd')


def test_fermi_dirac_time_function(signal_complex):
    signal = signal_complex.real
    time = np.arange(0, 1000, 1)
    t_0 = 500
    t_width = 20
    f = fermi_dirac(time, t_0, t_width)
    signal_damped = f * signal
    assert np.isclose(signal_damped[0], signal[0])
    assert np.isclose(signal_damped[-1], 0.0)


def test_smoothing_function():
    data = np.array([1, 2, 2.5, 4, 5.5, 6.5, 7, 8, 7, 2])

    res1 = smoothing_function(data, window_size=1, window_type='boxcar')
    assert np.allclose(res1, data)

    res2 = smoothing_function(data, window_size=2, window_type='boxcar')
    assert len(res2) == len(data)
    assert np.allclose(res2[0], 1)
    assert np.allclose(res2[1], 1.5)
    assert np.allclose(res2[2], 2.25)

    res3 = smoothing_function(data, window_size=3, window_type='boxcar')
    assert len(res3) == len(data)
    assert np.allclose(res3[0], 1.5)
    assert np.allclose(res3[1], 5.5/3)
    assert np.allclose(res3[2], 8.5/3)
    assert np.allclose(res3[-1], 4.5)


def test_align_structure():

    # randomly rotated Al FCC cubic cell
    atoms = bulk('Al', 'fcc', cubic=True).repeat(2)
    ref_cell = atoms.cell[:].copy()
    atoms.rotate(42, [1, 2, 5], rotate_cell=True)
    print(atoms.cell[:])
    align_structure(atoms)
    assert np.isclose(atoms.cell[0, 1], 0)
    assert np.isclose(atoms.cell[0, 2], 0)
    assert np.isclose(atoms.cell[1, 2], 0)
    assert np.allclose(atoms.cell, ref_cell)
    print(atoms.cell[:])

    # BCC primtive cell
    atoms = bulk('Ti', 'bcc', a=3.3).repeat(2)
    print(atoms.cell[:])
    align_structure(atoms)
    assert np.isclose(atoms.cell[0, 1], 0)
    assert np.isclose(atoms.cell[0, 2], 0)
    assert np.isclose(atoms.cell[1, 2], 0)
    print(atoms.cell[:])

    # strange cell which fails with very low tolerance
    cell = np.array([[6.66725037e+01, -7.15537500e-02, 3.71540563e-08],
                     [1.40460691e-01,  6.63955753e+01, 5.54413709e-02],
                     [5.91136223e-02, -3.04975220e-02, 4.73122339e+01]])
    atoms = bulk('Al', 'fcc', cubic=True).repeat(2)
    atoms.set_cell(cell, scale_atoms=True)
    align_structure(atoms, atol=1e-5)


def test_index_offset():
    prim = bulk('Ti', 'hcp')
    prim.set_array('basis_index', np.array([0, 1]))
    supercell = prim.repeat((4, 3, 2))

    # check indices
    offset, index = get_offset_index(prim, supercell)
    assert np.allclose(index, supercell.get_array('basis_index'))

    # fail if positions dont match
    supercell.positions[0, 0] += 0.03
    with pytest.raises(ValueError):
        offset, index = get_offset_index(prim, supercell)

    # works again if using higher tolerenaces
    offset, index = get_offset_index(prim, supercell, tol=0.05)
    assert np.allclose(index, supercell.get_array('basis_index'))
