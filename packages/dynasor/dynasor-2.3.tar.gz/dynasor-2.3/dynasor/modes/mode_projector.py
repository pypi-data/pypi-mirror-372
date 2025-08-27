from __future__ import annotations
from typing import Optional

import numpy as np
import warnings
import pickle
import itertools

from ase.calculators.singlepoint import SinglePointCalculator
from ase.units import fs
from ase import Atoms
from numpy.typing import NDArray

from dynasor.units import radians_per_fs_to_THz
from dynasor.tools.structures import get_displacements
from .tools import get_dynamical_matrix, group_eigvals, symmetrize_eigenvectors
from .qpoint import QPoint
from .atoms import Prim, Supercell
from ..qpoints.tools import get_commensurate_lattice_points


class ModeProjector:
    """
    The :class:`ModeProjector` maps between real atomic displacements `u` and
    complex mode coordinates `Q`.

    Some special python methods are implemented. The `__str__` and `__repr__`
    provides useful info. :class:`QPoint` objects are representations of a
    single q-point and associated information and can be accessed either by
    call providing a reduced wavevector

    >>> mp((1/2, 0, 0))  # doctest: +SKIP

    or by index corresponding to reduced q-point accessible from
    :attr:`~ModeProjector.q_reduced`

    >>> mp[2]  # doctest: +SKIP

    In addition to mode coordinates `Q` the class can also map the atomic
    velocities `v` to mode momenta `P` as well as atomic forces `f` to mode
    forces `F`. The class can also map back.  This mapping is done using
    getters and setters.  Internally only Q, P and F are stored

    >>> Q = mp.get_Q()  # doctest: +SKIP
    >>> mp.set_u(u)  # doctest: +SKIP

    In addition, the forces corresponding to the harmonic forces can be
    accessed by :meth:`~ModeProjector.get_f_harmonic()` and
    :meth:`~ModeProjector.get_F_harmonic()`. For ASE Atoms objects the
    displacments etc. can be updated and applied by

    >>> mp.update_from_atoms(atoms)  # doctest: +SKIP
    >>> atoms = mp.get_atoms(harmonic_forces=False)  # doctest: +SKIP

    The shapes for each property uses the follwoing varaibles

    * `N`: Number of atoms in supercell
    * `Nu`: unit cells (`N/Np`)
    * `Np`: primitive basis atoms (`N/Nu`)
    * `Nb`: bands (`Np*3`)
    * `Nq`: q-points (`Nu`)

    Please consult the documentation or the specific getters and setters to see
    the exact transformations used.

    Units
    ^^^^^
    The internal units in dynasor are Å, fs and eV. All frequencies are angular
    (a.k.a. the "physicist's convention" with 2π included). These are the units
    dynasor will expect and return. In, e.g., print functions conventional units
    such fs, Å, THz, Da, meV are commonly used.

    **Mass:**
    The internal unit choice (eV, Å, fs) means that the mass unit is not Dalton
    but rather 0.009648533290731906 Da.
    We refer to this unit as the "dynasor mass unit" (dmu),
    i.e., 1 Da = 103.64269572045423 dmu.
    As a user you will only see this unit in the output of :class:`ModeProjector` objects.
    Masses provided via, e.g., ASE Atoms objects are converted internally.

    **Waves:**
    dynasor reports and expects spatial (angular) frequencies in rad/Å and temporal (angular)
    frequencies in rad/fs. This follows the often-used convention in physics to include the
    factor of 2π in the wave vectors. For instance the wavelength is given by λ=2π/q.

    **Mode amplitudes:**
    Mode amplitudes are reported in Å√dmu = fs√eV.

    **Velocities:**
    For modes the momenta are reported in Å√dmu/fs or just √eV
    while atomic velocities are reported in Å/fs.

    **Mode forces:**
    The force is defined as the derivative of the momenta with respect to time
    so the unit used when reporting mode forces is Å√dmu/fs² (or √eV/fs).

    Internal arrays
    ^^^^^^^^^^^^^^^
    For the curious, the internal data arrays are

    * :attr:`primitive`, :attr:`supercell`, :attr:`force_constants` (input)
    * :attr:`_q`, :attr:`q_minus` (reduced q-points and which q-points are related by inversion)
    * :attr:`_D`, :attr:`_w2`, :attr:`_W`
      (dynamical matrices, frequencies (ev/Å²/Da), polarization vectors)
    * :attr:`_X` (eigenmodes which are mass weighted "polarization vectors" in the supercell)
    """
    def __init__(self, primitive: Atoms, supercell: Atoms, force_constants: NDArray[float]):
        """The mode projector is initialized by a primitive cell and a
        supercell as well as harmonic force constants.

        The force constants are assumed to be in units of eV/Å² as returned
        from phonopy. Be careful about the permutations when working with force
        constants and atoms object from different codes.

        Parameters
        ----------
        primitive
            Primitive cell. Note that the masses are stored internally as
            Dalton in ASE but will be converted to the internal dynasor
            mass unit (dmu).
        supercell
            Ideal supercell corresponding to the force constants.
        force_constants
            Force constants for the supercell in eV/Å² as a `(N, N, 3, 3)` array
            where `N` is `len(supercell)`.
        """
        if len(primitive) == len(supercell):
            warnings.warn('Primitive and supercell have the same size')
        elif len(primitive) > len(supercell):
            raise ValueError('Primitive cell larger than supercell')
        elif not (len(supercell) / len(primitive)).is_integer():
            raise ValueError('supercell size is not multiple of primitive size')

        if len(supercell) != len(force_constants):
            raise ValueError('force constants shape is not compatible with supercell size')

        if force_constants.shape != (len(supercell), len(supercell), 3, 3):
            raise ValueError('force constants shape should be (N, N, 3, 3)')

        self.primitive = Prim(primitive)
        self.supercell = Supercell(supercell, primitive)
        self.force_constants = force_constants

        # Find q-points in reduced primitive cell coordinates
        q_integer = get_commensurate_lattice_points(self.supercell.P.T)
        q_reduced = np.dot(q_integer, self.supercell.P_inv.T)
        self._q = np.array(sorted(tuple(q) for q in q_reduced))

        # The equivalent q-point corresponding to -q
        self._q_minus = [[tuple(q) for q in self._q].index(tuple((-q) % 1)) for q in self._q]

        # Construct dynamical matrix and diagonalize at each q-point
        self._D, self._w2, self._W = [], [], []
        for qi, q in enumerate(self._q):

            D = get_dynamical_matrix(
                    self.force_constants, self.supercell.offsets, self.supercell.indices,
                    q.astype(np.float64))

            if qi == self.q_minus[qi]:
                assert np.allclose(D.imag, 0)
                D = D.real

            D = np.einsum('ijab,i,j->ijab',
                          D, self.primitive.masses**-0.5, self.primitive.masses**-0.5)
            D_matrix = D.transpose(0, 2, 1, 3).reshape(-1, self.primitive.n_atoms * 3)
            assert np.allclose(D_matrix, D_matrix.T.conj())
            w2, W = np.linalg.eigh(D_matrix)
            W = W.T.reshape(-1, self.primitive.n_atoms, 3)

            self._D.append(D)
            self._w2.append(w2)
            self._W.append(W)

        self._D = np.array(self._D)
        self._w2 = np.array(self._w2)
        self._W = np.array(self._W)

        # Post check basic symmetries, group eigenvalues and try to make degenerate modes nicer
        for q, q_minus in enumerate(self.q_minus):
            q_minus = self.q_minus[q]

            assert np.allclose(self._D[q], self._D[q_minus].conj())
            assert np.allclose(self._w2[q], self._w2[q_minus])

            # tolerances for grouping and sorting eigenvalues and eigenvectors
            round_decimals = 12
            tolerance = 10**(-round_decimals)

            for group in group_eigvals(self._w2[q], tolerance**0.5):
                W = symmetrize_eigenvectors(self._W[q, group])

                # Try to order them
                W_sort = W.copy().transpose(0, 2, 1).reshape(len(W), -1)
                # abs is because we want to consider the magnitude
                # - (minus) basically reverts the sort order to place largest first
                # T is just because how lexsort works, we want to consider each
                #     atom and direction as a key for the bands
                # -1 is because we want to make the x-direction of the first
                #     atom the mist significant key
                # At the end the first band should have the largest magnitude
                #     for the first atom in x
                argsort = np.lexsort(np.round(-np.abs(W_sort).T[::-1], round_decimals))
                self._W[q, group] = W[argsort]

            self._W[q_minus] = self._W[q].conj()

        # Construct supercell projection matrix
        # q_ks = X_ksna u_na
        self._X = np.zeros((len(self._q), self.primitive.n_atoms * 3, self.supercell.n_atoms, 3),
                           dtype=np.complex128)

        for index in range(self.supercell.n_atoms):
            i, N = self.supercell.indices[index], self.supercell.offsets[index]
            for q, s, a in itertools.product(
                    range(len(self._q)), range(self.primitive.n_atoms * 3), range(3)):
                phase = np.exp(-1j * 2*np.pi * self._q[q] @ N)
                self._X[q, s, index, a] = (
                        self.primitive.masses[i]**0.5 * phase * self._W[q, s, i, a].conj())
        self._X /= (self.supercell.n_atoms / self.primitive.n_atoms)**0.5

        # Init arrays to hold Q, P and F
        self._Q = np.zeros((len(self._q), self.primitive.n_atoms*3), dtype=np.complex128)
        self._P = np.zeros_like(self._Q)
        self._F = np.zeros_like(self._Q)

    def __str__(self):
        strings = ['### ModeProjector ###']
        strings += [f'{self.supercell}']
        strings += [f'{self.primitive}']
        string = '\n'.join(strings)

        # ASCII DOS!
        width = 80
        height = 24
        dos = np.full((height, width), ' ')

        THz = self.omegas * radians_per_fs_to_THz

        hist, bins = np.histogram(THz.flat, bins=width)

        for i, h in enumerate(hist):
            dos[np.round(h * (height - 1) / hist.max()).astype(int), i] = '+'  # '·' or 'x'

        dos = dos[::-1]
        dos[-1, dos[-1] == ' '] = '-'
        dos = '\n'.join([''.join(d) for d in dos])

        string += f'\n{dos}'
        string += f'\n|{THz.min():<10.2f} THz' + ' '*(width - 26) + f'{THz.max():>10.2f}|'

        return string

    def __repr__(self):
        return str(self)

    def __getitem__(self, q) -> QPoint:
        """Returns the q-point object based on its index"""
        if q < 0 or q >= len(self._q):
            raise IndexError
        return QPoint(q, self)

    def __call__(self, qpoint) -> QPoint:
        """Tries to find a matching q-point based on reduced coordinate"""
        qpoint = np.array(qpoint).astype(np.float64) % 1
        for q, qpoint2 in enumerate(np.array(self._q).astype(np.float64)):
            if np.allclose(qpoint, qpoint2):
                return QPoint(q, self)
        raise ValueError('qpoint not compatible, check mp.q_reduced')

    # Getters ans setters for internal mutable arrays
    def get_Q(self) -> NDArray[float]:
        """The mode coordinate amplitudes in Å√dmu."""
        return self._Q.copy()

    def get_P(self) -> NDArray[float]:
        """The mode momentum amplitudes in √eV."""
        return self._P.copy()

    def get_F(self) -> NDArray[float]:
        """The mode force amplitudes in eV/Å√dmu."""
        return self._F.copy()

    def get_F_harmonic(self) -> NDArray[float]:
        r"""The harmonic mode forces, computed as :math:`-\omega^2 * Q` in eV/Å√dmu."""
        return -self._w2 * self.get_Q()

    def set_Q(self, Q: NDArray[float]) -> None:
        """Sets the internal mode coordinates :math:`Q`.

        The functions ensures :math:`Q(-q)=Q^*(q)`.
        """
        # This ensures that stuff like mp.set_Q(0) works while not updating the
        # array until the assert
        Q_new = self.get_Q()
        Q_new[:] = Q
        if not np.allclose(np.conjugate(Q_new), Q_new[self.q_minus]):
            raise ValueError('Supplied Q does not fulfill Q(-q) = Q(q)*')
        self._Q[:] = Q_new

    def set_P(self, P: NDArray[float]) -> None:
        """Sets the internal mode momenta :math:`P`.

        The functions ensures :math:`P(-q)=P^*(q)`
        """
        P_new = self.get_P()
        P_new[:] = P
        if not np.allclose(np.conjugate(P_new), P_new[self.q_minus]):
            raise ValueError('Supplied P does not fulfill P(-q) = P(q)*')
        self._P[:] = P_new

    def set_F(self, F: NDArray[float]) -> None:
        """Sets the internal mode forces :math:`F`.

        The functions ensures :math:`F(-q)=F^*(q)`.
        """
        F_new = self.get_F()
        F_new[:] = F
        if not np.allclose(np.conjugate(F_new), F_new[self.q_minus]):
            raise ValueError('Supplied F does not fulfill F(-q) = F(q)*')
        self._F[:] = F_new

    def get_u(self) -> NDArray[float]:
        """The atomic displacements in Å."""
        u = np.einsum('ksna,ks,n->na', self._X.conj(), self._Q, 1 / self.supercell.masses)
        assert np.allclose(u.imag, 0)
        return u.real

    def get_v(self) -> NDArray[float]:
        """The atomic velocities in Å/fs."""
        v = np.einsum('ksna,ks,n->na', self._X, self._P, 1 / self.supercell.masses)
        assert np.allclose(v.imag, 0)
        return v.real

    def get_f(self) -> NDArray[float]:
        """The atomic forces in eV/Å."""
        f = np.einsum('ksna,ks->na', self._X, self._F)
        assert np.allclose(f.imag, 0)
        return f.real

    def get_f_harmonic(self) -> NDArray[float]:
        """The harmonic atomic forces for the current displacements."""
        F_harmonic = self.get_F_harmonic()
        f_harmonic = np.einsum('ksna,ks->na', self._X, F_harmonic)
        assert np.allclose(f_harmonic.imag, 0)
        return f_harmonic.real

    def set_u(self, u: NDArray[float]) -> None:
        """Sets the internal mode coordinates :math:`Q` given the atomic displacements :math:`u`.

        .. math::

            Q = X u

        Parameters
        ----------
        u
            The atomic displacements in Å.
        """
        Q = np.einsum('ksna,na->ks', self._X, u)
        self.set_Q(Q)

    def set_v(self, v: NDArray[float]) -> None:
        """Sets the internal mode momenta :math:`P` given the atomic velocities :math:`v`.

        .. math::

            P = X^* * v

        Parameters
        ----------
        v
            The atomic velocities in Å/fs.
        """
        P = np.einsum('ksna,na->ks', self._X.conj(), v)
        self.set_P(P)

    def set_f(self, f: NDArray[float]) -> None:
        """Sets the internal mode forces :math:`F` given the atomic forces :math:`f`.

        .. math::

            F = X^* * f / m

        Parameters
        ----------
        f
            The atomic forces in eV/Å.
        """
        F = np.einsum('ksna,na,n->ks', self._X.conj(), f, 1 / self.supercell.masses)
        self.set_F(F)

    # Convenience functions to handle ASE Atoms objects
    def get_atoms(self, harmonic_forces: Optional[bool] = False) -> Atoms:
        r"""Returns ASE :class:`Atoms` object with displacement,
        velocities, forces, and harmonic energies.

        Parameters
        ----------
        harmonic_forces
            Whether the forces should be taken from the internal `F` or via `-\omega^2 Q`.
        """
        atoms = self.supercell.to_ase()
        atoms.positions += self.get_u()
        atoms.set_velocities(self.get_v() / fs)
        E = self.potential_energies.sum()
        f = self.get_f_harmonic() if harmonic_forces else self.get_f()

        atoms.calc = SinglePointCalculator(
                energy=E, forces=f, stress=None, magmoms=None, atoms=atoms)

        return atoms

    def update_from_atoms(self, atoms: Atoms) -> None:
        """Updates the :class:`ModeProjector` objects with displacments, velocities,
        and forces from an ASE :class:`Atoms` object.

        Checks for an attached calculator in the first place and next for a forces array.

        If no data sets corresponding array to zeros.

        The masses and velocities are converted to dynasor units internally.
        """

        u = get_displacements(atoms, self.supercell)
        if np.max(np.abs(u)) > 2.0:
            warnings.warn('Displacements larger than 2Å. Is the atoms object permuted?')
        self.set_u(u)
        self.set_v(atoms.get_velocities() * fs)
        try:
            self.set_f(atoms.get_forces())
        except RuntimeError:
            if 'forces' in atoms.arrays:
                self.set_f(atoms.arrays['forces'])
            else:
                self.set_f(np.zeros_like(atoms.positions))

    # properties
    @property
    def q_minus(self) -> NDArray[float]:
        """The index of the corresponding counter-propagating mode (:math:`-q`)."""
        return self._q_minus.copy()

    @property
    def q_reduced(self) -> NDArray[float]:
        """The q-points in reduced coordinates.

        For example a zone boundary mode would be (1/2, 0, 0)
        """
        return self._q.astype(float)

    @property
    def q_cartesian(self) -> NDArray[float]:
        """The q-points in cartesian coordinates with unit of rad/Å (2π included)."""
        return 2 * np.pi * self.q_reduced @ self.primitive.inv_cell

    @property
    def omegas(self) -> NDArray[float]:
        """The frequencies of each mode in rad/fs.

        Following convetion negative values indicate imaginary frequencies.
        """
        return np.sign(self._w2) * np.sqrt(np.abs(self._w2))

    @property
    def polarizations(self) -> NDArray[float]:
        """The polarization vectors for each mode `(Nq, Nb, Np, 3)`."""
        return self._W

    @property
    def eigenmodes(self) -> NDArray[float]:
        """The eigenmodes in the supercell as `(Nq, Nb, N, 3)`-array

        The eigenmodes include the masses such that :math:`Q = X u`
        where :math:`u` are the supercell displacements.
        """
        return self._X

    @property
    def potential_energies(self) -> NDArray[float]:
        """Potential energy per mode as `(Nq, Nb)`-array.

        The potential energies are defined as :math:`1/2 Q Q^*` and should equal
        :math:`1/2 k_B T` in equilibrium for a harmonic system.
        """
        return 1 / 2 * np.abs(self._Q) ** 2 * self._w2

    @property
    def kinetic_energies(self) -> NDArray[float]:
        """Kinetic energy per mode as `(Nq, Nb)`-array.

        The kinetic energies are defined as :math:`1/2 P P^*`. Should equal
        :math:`1/2 k_B T` in equilibrium.`
        """
        return 1 / 2 * np.abs(self._P)**2

    @property
    def virial_energies(self) -> NDArray[float]:
        """The virial energies per mode as `(Nq, Nb)`-array.

        The virial energies are defined here as :math:`-1/2 Q F`, which should have an
        expectation value of :math:`1/2 k_B T` per mode in equilibrium. For a harmonic
        system this is simply equal to the potential energy. This means that
        the virial energy can be used to monitor the anharmonicity or
        define a measure of the potential energy.
        """
        return -1 / 2 * self._Q * self._F

    def write(self, file_name: str) -> None:
        """Uses pickle to write mode projector to file."""
        with open(file_name, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def read(cls, file_name: str) -> ModeProjector:
        """Return :class:`ModeProjector` instance from pickle file
        that was saved using :func:`~ModeProjector.write`."""
        with open(file_name, 'rb') as f:
            mp = pickle.load(f)
        return mp
