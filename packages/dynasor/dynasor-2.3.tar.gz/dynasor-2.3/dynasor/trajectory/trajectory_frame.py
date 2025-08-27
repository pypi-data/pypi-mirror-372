from dataclasses import dataclass
from typing import Optional
import numpy as np
from numpy.typing import NDArray


@dataclass
class ReaderFrame:
    """Trivial data struct holding MD-data for one time frame.

    Parameters
    ----------
    frame_index
        Trajectory index of the snapshot (frame).
    cell
        Simulation cell as 3 row vectors (Å).
    n_atoms
        Number of atoms.
    positions
        Particle positions as 3xn_atoms array (Å).
    velocities
        Particle velocities as 3xn_atoms array (Å/fs);
        may not be available, depending on reader and trajectory file format.
    atom_types
        Array with the type of each atom;
        may not be available, depending on reader and trajectory file format.
    """
    frame_index: int
    cell: NDArray[float]
    n_atoms: int
    positions: NDArray[float]
    velocities: Optional[NDArray[float]] = None
    atom_types: Optional[NDArray[str]] = None


class TrajectoryFrame:
    """
    Class holding positions and optionally velocities split by atom type
    for one snapshot (frame) in a trajectory.

    Attributes
    ----------
    * `positions_by_type`
    * `velocities_by_type`

    such that, e.g.,
    `positions_by_type['Cs']` is a numpy array with shape `(n_atoms_Cs, 3)` and
    `positions_by_type['Pb']` is a numpy array with shape `(n_atoms_Pb, 3)`

    Parameters
    ----------
    atomic_indices
        Dictionary specifying which indices (values) belong to which atom type (keys).
    frame_index
        Trajectory index of the snapshot (frame).
    positions
        Positions as an array with shape `(n_atoms, 3)`.
    velocities
        Velocities as an array with shape `(n_atoms, 3)`; defaults to `None`.
    """

    def __init__(self,
                 atomic_indices: dict[str, list[int]],
                 frame_index: int,
                 positions: NDArray[float],
                 velocities:  Optional[NDArray[float]] = None):
        self._frame_index = frame_index

        self.positions_by_type = dict()
        for atom_type, indices in atomic_indices.items():
            self.positions_by_type[atom_type] = positions[indices, :].copy()

        if velocities is not None:
            self.velocities_by_type = dict()
            for atom_type, indices in atomic_indices.items():
                self.velocities_by_type[atom_type] = velocities[indices, :].copy()
        else:
            self.velocities_by_type = None

    def get_positions_as_array(self, atomic_indices: dict[str, list[int]]) -> NDArray[float]:
        """
        Return the full positions array with shape ``(n_atoms, 3)``.

        Parameters
        ---------
        atomic_indices
            Dictionary specifying which indices (values) belong to which atom type (keys).
        """

        # check that atomic_indices is complete
        n_atoms = np.max([np.max(indices) for indices in atomic_indices.values()]) + 1
        all_inds = [i for indices in atomic_indices.values() for i in indices]
        if len(all_inds) != n_atoms or len(set(all_inds)) != n_atoms:
            raise ValueError('atomic_indices is incomplete')

        # collect positions into a single array
        x = np.empty((n_atoms, 3))
        for atom_type, indices in atomic_indices.items():
            x[indices, :] = self.positions_by_type[atom_type]
        return x

    def get_velocities_as_array(self, atomic_indices: dict[str, list[int]]) -> NDArray[float]:
        """
        Return the full velocities array with shape ``(n_atoms, 3)``.

        Parameters
        ---------
        atomic_indices
            Dictionary specifying which indices (values) belong to which atom type (keys).
        """

        # check that atomic_indices is complete
        n_atoms = np.max([np.max(indices) for indices in atomic_indices.values()]) + 1
        all_inds = [i for indices in atomic_indices.values() for i in indices]
        if len(all_inds) != n_atoms or len(set(all_inds)) != n_atoms:
            raise ValueError('atomic_indices is incomplete')

        # collect velocities into a single array
        v = np.empty((n_atoms, 3))
        for atom_type, indices in atomic_indices.items():
            v[indices, :] = self.velocities_by_type[atom_type]
        return v

    @property
    def frame_index(self) -> int:
        """ Index of the frame. """
        return self._frame_index

    def __str__(self) -> str:
        s = [f'Frame index {self.frame_index}']
        for key, val in self.positions_by_type.items():
            s.append(f'  positions  : {key}   shape : {val.shape}')
        if self.velocities_by_type is not None:
            for key, val in self.velocities_by_type.items():
                s.append(f'  velocities : {key}   shape : {val.shape}')
        return '\n'.join(s)

    def __repr__(self) -> str:
        return str(self)

    def _repr_html_(self) -> str:
        s = [f'<h3>{self.__class__.__name__}</h3>']
        s += ['<table border="1" class="dataframe">']
        s += ['<thead><tr><th style="text-align: left;">Field</th>'
              '<th>Value/Shape</th></tr></thead>']
        s += ['<tbody>']
        s += [f'<tr><td style="text-align: left;">Index</td><td>{self.frame_index}</td></tr>']
        for key, val in self.positions_by_type.items():
            s += [f'<tr><td style="text-align: left;">Positions {key}</td>'
                  f'<td>{val.shape}</td></tr>']
        if self.velocities_by_type is not None:
            for key, val in self.velocities_by_type.items():
                s += [f'<tr><td style="text-align: left;">Velocities {key}</td>'
                      f'<td>{val.shape}</td></tr>']
        s += ['</tbody>']
        s += ['</table>']
        return '\n'.join(s)
