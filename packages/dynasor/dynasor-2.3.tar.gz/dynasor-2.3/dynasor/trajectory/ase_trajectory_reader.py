from itertools import count
from typing import Optional
import numpy as np
from ase import io
from dynasor.trajectory.abstract_trajectory_reader import AbstractTrajectoryReader
from dynasor.trajectory.trajectory_frame import ReaderFrame


class ASETrajectoryReader(AbstractTrajectoryReader):
    """Read ASE trajectory file

    ...

    Parameters
    ----------
    filename
        Name of input file.
    length_unit
        Unit of length for the input trajectory (``'Angstrom'``, ``'nm'``, ``'pm'``, ``'fm'``).
    time_unit
        Unit of time for the input trajectory (``'fs'``, ``'ps'``, ``'ns'``).
    """

    def __init__(
        self,
        filename: str,
        length_unit: Optional[str] = 'Angstrom',
        time_unit: Optional[str] = 'fs',
    ):
        self._frame_index = count(0)
        self._atoms = io.iread(filename, index=':')

        # setup units
        self.set_unit_scaling_factors(length_unit, time_unit)

    def __iter__(self):
        return self

    def close(self):
        pass

    def __next__(self):
        ind = next(self._frame_index)
        a = next(self._atoms)
        if 'momenta' in a.arrays:
            vel = self.v_factor * a.get_velocities()
        else:
            vel = None
        return ReaderFrame(
            frame_index=ind,
            n_atoms=len(a),
            cell=self.x_factor * a.cell.array.copy('F'),
            positions=self.x_factor * a.get_positions(),
            velocities=vel,
            atom_types=np.array(list(a.symbols)),
        )
