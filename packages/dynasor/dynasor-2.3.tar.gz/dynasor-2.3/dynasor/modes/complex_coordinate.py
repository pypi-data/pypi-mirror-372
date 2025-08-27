from __future__ import annotations  # for 3.9 for typehint 'Band' in cc.band
from typing import TYPE_CHECKING
import math

import numpy as np

from ..units import radians_per_fs_to_THz


if TYPE_CHECKING:
    from .band import Band


class ComplexCoordinate:
    """Class to work with the in general complex coordinates of lattice dynamics.

    Can be cast to complex by `complex(cc)`

    Example
    -------
    >>> cc.complex = 1.7j  # doctest: +SKIP
    >>> cc.amplitude = 3.8  # doctest: +SKIP
    >>> cc.phase = 2*np.pi  # doctest: +SKIP
    """

    def __init__(self, q, s, mp):
        """The complex coordinate belongs to a q-point and band."""
        self._q = q
        self._s = s
        self._mp = mp

    def __repr__(self):
        return str(self)

    def __complex__(self):
        return complex(getattr(self._mp, 'get_' + self.__class__.__name__)()[self._q, self._s])

    @property
    def band(self) -> 'Band':
        """The band to which this coordinate belongs to."""
        return self._mp[self._q][self._s]

    @property
    def complex(self):
        """The complex coordinate as a complex number."""
        return complex(self)

    @complex.setter
    def complex(self, C):
        C = complex(C)
        prop = self.__class__.__name__

        val = getattr(self._mp, 'get_' + prop)()

        if self._mp[self._q].is_real:
            assert np.isclose(C.imag, 0)
            q2 = self._q
        else:
            q2 = self._mp[self._q].q_minus.index

        val[self._q, self._s] = C
        val[q2, self._s] = C.conjugate()

        getattr(self._mp, 'set_' + prop)(val)

    @property
    def phase(self):
        """The phase of the complex coordinate."""
        c = complex(self)
        return math.atan2(c.imag, c.real)

    @phase.setter
    def phase(self, phase):
        C = complex(self)
        C = np.abs(C) * np.exp(1j * phase)
        self.complex = C

    @property
    def amplitude(self):
        """The amplitude of the complex coordinate."""
        c = complex(self)
        return np.abs(c)

    @amplitude.setter
    def amplitude(self, amplitude):
        C = amplitude * np.exp(1j * self.phase)
        self.complex = C


class Q(ComplexCoordinate):
    def __str__(self):
        s = ['### Mode coordinate Q ###']
        s += [f'band:      [{self.band.index}] {self.band.omega * radians_per_fs_to_THz:.2f} THz']
        s += [f'q-point:   [{self.band.qpoint.index}] {self.band.qpoint.q_reduced}']
        s += [f'Value:     {self.complex:.2f} Å√dmu']
        s += [f'Amplitude: {self.amplitude:.2f} Å√dmu']
        s += [f'Phase:     {self.phase:.2f} radians']
        return '\n'.join(s)


class P(ComplexCoordinate):
    def __str__(self):
        s = ['### Mode momentum P ###']
        s += [f'band:      [{self.band.index}] {self.band.omega * radians_per_fs_to_THz:.2f} THz']
        s += [f'q-point:   [{self.band.qpoint.index}] {self.band.qpoint.q_reduced}']
        s += [f'Value:     {self.complex:.2f} Å√dmu/fs']
        s += [f'Amplitude: {self.amplitude:.2f} Å√dmu/fs']
        s += [f'Phase:     {self.phase:.2f} radians']
        return '\n'.join(s)


class F(ComplexCoordinate):
    def __str__(self):
        s = ['### Mode force F ###']
        s += [f'band:      [{self.band.index}] {self.band.omega * radians_per_fs_to_THz:.2f} THz']
        s += [f'q-point:   [{self.band.qpoint.index}] {self.band.qpoint.q_reduced}']
        s += [f'Value:     {self.complex:.2f} Å√dmu/fs²']
        s += [f'Amplitude: {self.amplitude:.2f} Å√dmu/fs²']
        s += [f'Phase:     {self.phase:.2f} radians']
        return '\n'.join(s)
