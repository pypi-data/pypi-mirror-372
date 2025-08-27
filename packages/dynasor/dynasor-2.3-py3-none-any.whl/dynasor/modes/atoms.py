from typing import Union
import numpy as np
from ase.units import fs
from ase import Atoms
from numpy.typing import NDArray
from .tools import inv
from ..units import Dalton_to_dmu


class DynasorAtoms:
    """Dynasor's representation of a structure."""
    def __init__(self, atoms: Atoms):
        """Initialized using an ASE Atoms object"""
        self._atoms = atoms

    @property
    def pos(self) -> NDArray[float]:
        """Cartesian positions."""
        return self._atoms.positions.copy()

    @property
    def positions(self) -> NDArray[float]:
        """Cartesian positions."""
        return self.pos

    @property
    def spos(self) -> NDArray[float]:
        """Reduced (or scaled) positions of atoms."""
        return self._atoms.get_scaled_positions()

    @property
    def scaled_positions(self) -> NDArray[float]:
        """Reduced (or scaled) positions of atoms."""
        return self.spos

    @property
    def cell(self) -> NDArray[float]:
        """Cell of atoms with cell vectors as rows."""
        return self._atoms.cell.array.copy()

    @property
    def inv_cell(self) -> NDArray[float]:
        """The inverse cell transpose so the inverse cell vectors are rows, no 2pi."""
        return np.linalg.inv(self._atoms.cell.array).T

    @property
    def numbers(self) -> NDArray[int]:
        """Chemical number for each atom, e.g., 1 for H, 2 for He etc."""
        return self._atoms.numbers.copy()

    @property
    def masses(self) -> NDArray[float]:
        """Masses of atoms in dmu."""
        return self._atoms.get_masses() / fs ** 2  # In eVfs²/Å²

    @property
    def volume(self) -> float:
        """Volume of cell."""
        return self._atoms.get_volume()

    @property
    def n_atoms(self) -> int:
        """Number of atoms."""
        return len(self._atoms)

    @property
    def symbols(self) -> list[str]:
        """List of chemical symbol for each element."""
        return list(self._atoms.symbols)

    def to_ase(self) -> Atoms:
        """Converts the internal Atoms to ASE :class:`Atoms`."""
        return Atoms(cell=self.cell, numbers=self.numbers, positions=self.positions, pbc=True)

    def __repr__(self) -> str:
        return str(self)


class Prim(DynasorAtoms):
    def __str__(self):
        strings = [f"""Primitive cell:
Number of atoms:        {self.n_atoms}
Volume:                 {self.volume:.3f}
Atomic species present: {set(self.symbols)}
Atomic numbers present: {set([int(n) for n in self.numbers])}
Cell:
[[{self.cell[0, 0]:<20}, {self.cell[0, 1]:<20}, {self.cell[0, 2]:<20}],
 [{self.cell[1, 0]:<20}, {self.cell[1, 1]:<20}, {self.cell[1, 2]:<20}],
 [{self.cell[2, 0]:<20}, {self.cell[2, 1]:<20}, {self.cell[2, 2]:<20}]]
"""]
        strings.append(f"{'Ind':<5}{'Sym':<5}{'Num':<5}{'Mass (Da)':<10}{'x':<10}{'y':<10}{'z':<10}"
                       f"{'a':<10}{'b':<10}{'c':<10}")
        atom_s = []
        for i, p, sp, m, n, s in zip(
                range(self.n_atoms), self.positions, self.spos, self.masses / Dalton_to_dmu,
                self.numbers, [a.symbol for a in self.to_ase()]):
            atom_s.append(f'{i:<5}{s:<5}{n:<5}{m:<10.2f}{p[0]:<10.3f}{p[1]:<10.3f}{p[2]:<10.3f}'
                          f'{sp[0]:<10.3f}{sp[1]:<10.3f}{sp[2]:<10.3f}')

        strings = strings + atom_s

        string = '\n'.join(strings)

        return string


class Supercell(DynasorAtoms):
    """The supercell takes care of some mappings between the primitive and repeated structure.

    In particular the P-matrix connecting the cells as well as the offset-index of each atom is
    calculated.

    Note that the positions cannot be revovered as `offset x cell + basis` since the atoms get
    wrapped.

    Parameters
    ----------
    supercell
        Some ideal repetition of the primitive structure and possible wrapping.
    prim
        Primitive structure.
    """

    def __init__(self, supercell: Union[Atoms, DynasorAtoms], prim: Union[Atoms, DynasorAtoms]):
        self.prim = Prim(prim.copy())
        super().__init__(supercell)

        # determine P-matrix relating supercell to primitive cell
        from dynasor.tools.structures import get_P_matrix
        self._P = get_P_matrix(self.prim.cell, self.cell)  # P C = S
        self._P_inv = inv(self.P)

        # find the index and offsets for supercell using primitive as base unit
        from dynasor.tools.structures import get_offset_index
        self._offsets, self._indices = get_offset_index(prim, supercell, wrap=True)

    @property
    def P(self) -> NDArray[float]:
        """P-matrix is defined as dot(P, prim.cell) = supercell.cell"""
        return self._P.copy()

    @property
    def P_inv(self) -> NDArray[float]:
        """Inverse of `P`."""
        return self._P_inv.copy()

    @property
    def offsets(self) -> NDArray[float]:
        """The offset of each atom."""
        return self._offsets.copy()

    @property
    def indices(self) -> NDArray[int]:
        """The basis index of each atom"""
        return self._indices.copy()

    @property
    def n_cells(self) -> int:
        """Number of unit cells"""
        return self.n_atoms // self.prim.n_atoms

    def __str__(self):

        string = f"""Supercell:
Number of atoms:      {self.n_atoms}
Volume:               {self.volume:.3f}
Number of unit cells: {self.n_cells}
Cell:
[[{self.cell[0, 0]:<20}, {self.cell[0, 1]:<20}, {self.cell[0, 2]:<20}],
 [{self.cell[1, 0]:<20}, {self.cell[1, 1]:<20}, {self.cell[1, 2]:<20}],
 [{self.cell[2, 0]:<20}, {self.cell[2, 1]:<20}, {self.cell[2, 2]:<20}]]
P-matrix:
[[{self.P[0, 0]:<20}, {self.P[0, 1]:<20}, {self.P[0, 2]:<20}],
 [{self.P[1, 0]:<20}, {self.P[1, 1]:<20}, {self.P[1, 2]:<20}],
 [{self.P[2, 0]:<20}, {self.P[2, 1]:<20}, {self.P[2, 2]:<20}]]
{self.prim}
"""
        return string
