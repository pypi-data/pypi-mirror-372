import numpy as np

from dynasor.units import radians_per_fs_to_THz, radians_per_fs_to_meV, radians_per_fs_to_invcm
from dynasor.units import THz_to_meV, THz_to_invcm, meV_to_invcm


def test_units():

    assert np.isclose(THz_to_meV, 4.13567)
    assert np.isclose(THz_to_meV * meV_to_invcm, THz_to_invcm)

    assert np.isclose(radians_per_fs_to_THz, 1000 / (2 * np.pi))
    assert np.isclose(radians_per_fs_to_THz * THz_to_meV, radians_per_fs_to_meV)
    assert np.isclose(radians_per_fs_to_THz * THz_to_invcm, radians_per_fs_to_invcm)
