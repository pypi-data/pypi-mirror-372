import numpy as np
from numpy.typing import NDArray

from ..units import radians_per_fs_to_THz
from .band import Band


class QPoint:
    """Representation of a single q-point and properties.

    The bands can be accessed by, e.g., `qp[2]` to get band index 2 in the form
    of a :class:`~dynasor.modes.band.Band` object.

    Parameters
    ----------
    q
        q-point index.
    mp
        Mode project object.
    """
    def __init__(self, q_index: int, mp):
        self._mp = mp
        self._q = q_index

    def __str__(self):
        s = ['### q-point ###']
        s += [f'Index:       {self.index}']
        s += [f'Reduced:     {self.q_reduced}']
        s += ['Cartesian:   ['
              f'{self.q_cartesian[0]:.2f}, {self.q_cartesian[1]:.2f}, {self.q_cartesian[2]:.2f}'
              '] rad/Å']
        s += [f'Wavenumber:  {self.wavenumber:.2f} rad/Å']
        s += [f'Wavelength:  {self.wavelength:.2f} Å']
        s += [f'q-minus:     {self.q_minus.index} {self.q_minus.q_reduced}']
        s += [f'Real:        {self.is_real}']
        s += ['']
        s += ['Omegas:      ['
              ', '.join(f'{t * radians_per_fs_to_THz:.2f}' for t in self.omegas) + '] THz']
        return '\n'.join(s)

    def __repr__(self):
        return str(self)

    def __getitem__(self, s):
        if s >= self._mp.primitive.n_atoms * 3:
            raise IndexError
        return Band(self.index, s, self._mp)

    @property
    def q_minus(self):
        """The corresponding counter-propagating mode."""
        return self._mp[self._mp.q_minus[self.index]]

    @property
    def polarizations(self) -> NDArray[float]:
        """Slice, see :class:`~dynasor.ModeProjector`."""
        return self._mp.polarizations[self.index]

    @property
    def omegas(self) -> NDArray[float]:
        """Slice, see :class:`~dynasor.ModeProjector`."""
        return self._mp.omegas[self.index]

    @property
    def is_real(self) -> bool:
        """If the q-point has purely real mode coordinates, `q=-q`."""
        return self.index == self.q_minus.index

    @property
    def index(self) -> int:
        """q-point index corresponding to :class:`~dynasor.ModeProjector.q_reduced`."""
        return self._q

    @property
    def wavenumber(self) -> float:
        """Wavenumber of mode in rad/Å. """
        return np.linalg.norm(self._mp.q_cartesian[self.index])

    @property
    def wavelength(self) -> float:
        """Wavelength of mode in Å. """
        return np.inf if self.wavenumber == 0 else 2 * np.pi / self.wavenumber

    @property
    def q_reduced(self) -> NDArray[float]:
        """Slice, see :class:`~dynasor.ModeProjector`."""
        return self._mp.q_reduced[self.index]

    @property
    def q_cartesian(self) -> NDArray[float]:
        """Slice, see :class:`~dynasor.ModeProjector`."""
        return self._mp.q_cartesian[self.index]

    @property
    def eigenmodes(self) -> NDArray[float]:
        """Slice, see :class:`~dynasor.ModeProjector`."""
        return self._mp.eigenmodes[self.index]

    @property
    def potential_energies(self) -> NDArray[float]:
        """Slice, see :class:`~dynasor.ModeProjector`."""
        return self._mp.potential_energies[self.index]

    @property
    def kinetic_energies(self) -> NDArray[float]:
        """Slice, see :class:`~dynasor.ModeProjector`."""
        return self._mp.kinetic_energies[self.index]

    @property
    def virial_energies(self) -> NDArray[float]:
        """Slice, see :class:`~dynasor.ModeProjector`."""
        return self._mp.virial_energies[self.index]
