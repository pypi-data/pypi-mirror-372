"""This module contains convenient unit conversion factors.
Here, `radians_per_fs_to_invcm`, for example, can be used to convert
an angular frequency in units of radians/fs to a wavenumber in 1/cm, as
demonstrated by the code snippet below::

>>> # converting angular frequencies (omega) to wavenumbers in inverse cm
>>> import numpy as np
>>> omegas = np.linspace(0, 15, 100)
>>> frequencies_invcm = omegas * radians_per_fs_to_invcm
>>>
>>> # converting from inverse cm to meV
>>> frequencies_meV = frequencies_invcm / meV_to_invcm

In practice you can apply this conversion directly to, e.g., the frequencies
of a :class:`DynamicSample <sample.DynamicSample>` object.
"""
from math import pi
from ase.units import _c, invcm, fs

# Frequencies
meV_to_invcm = 1 / invcm / 1e3
r"""Conversion factor from meV (energy) to cm\ :math:`^{-1}` (wave numbers)."""

THz_to_invcm = 1e12 / _c / 1e2
r"""Conversion factor from THz (frequency) to cm\ :math:`^{-1}` (wave numbers)."""

THz_to_meV = 1e13 * invcm / _c
"""Conversion factor from THz (frequency) to meV (energy)."""

# Angular frequencies
radians_per_fs_to_THz = 1000 / (2 * pi)
"""Conversion factor from rad/fs (radians per femtosecond) to THz (frequency)."""

radians_per_fs_to_meV = radians_per_fs_to_THz * THz_to_meV
"""Conversion factor from rad/fs (radians per femtosecond) to meV (energy)."""

radians_per_fs_to_invcm = radians_per_fs_to_THz * THz_to_invcm
r"""Conversion factor from rad/fs (radians per femtosecond) to cm\ :math:`^{-1}` (wave numbers)."""

# Mass
Dalton_to_dmu = 1 / fs**2
"""Conversion factor from Daltons (SI mass unit) to the internal dynasor mass units."""
