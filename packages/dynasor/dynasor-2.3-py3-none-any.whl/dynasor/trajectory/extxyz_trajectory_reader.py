import concurrent.futures
from itertools import count
from typing import Optional
from ase import Atoms
from ase.io.extxyz import ixyzchunks
from dynasor.trajectory.abstract_trajectory_reader import AbstractTrajectoryReader
from dynasor.trajectory.trajectory_frame import ReaderFrame
import numpy as np


def chunk_to_atoms(chunk):
    atoms = chunk.build()
    return atoms


def iread(f, max_workers: Optional[int] = None) -> Atoms:
    """Reads extxyz in parallel using multiple processese.

    Parameters
    ----------
    f
        File object.
    max_workers
        Maximum number of processes.
    """

    # chunks are simple objects
    chunk_iterator = iter(ixyzchunks(f))

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as ex:

        buff = []
        for i in range(ex._max_workers):
            try:
                chunk = next(chunk_iterator)
                buff.append(ex.submit(chunk_to_atoms, chunk))
            except RuntimeError:
                pass
            except StopIteration:
                pass

        while True:
            if len(buff) == 0:
                break

            res = buff.pop(0)

            try:
                chunk = next(chunk_iterator)
                buff.append(ex.submit(chunk_to_atoms, chunk))
            except RuntimeError:
                pass
            except StopIteration:
                pass

            atoms = res.result()
            yield atoms


class ExtxyzTrajectoryReader(AbstractTrajectoryReader):
    """Read extend xyz trajectory file, typically produced by GPUMD

    This is a naive (and comparatively slow) parallel implementation which
    relies on the ASE xyz reader.

    Parameters
    ----------
    filename
        Name of input file.
    length_unit
        Unit of length for the input trajectory (``'Angstrom'``, ``'nm'``, ``'pm'``, ``'fm'``).
    time_unit
        Unit of time for the input trajectory (``'fs'``, ``'ps'``, ``'ns'``).
    max_workers
        Number of working processes; defaults to ``None``, which means that the number of
        processors on the machine is used.
    """

    def __init__(self,
                 filename: str,
                 length_unit: Optional[str] = None,
                 time_unit: Optional[str] = None,
                 max_workers: Optional[int] = None):

        # setup generator object
        self._fobj = open(filename, 'r')
        self._generator_xyz = iread(self._fobj, max_workers=max_workers)
        self._open = True
        self._frame_index = count(0)

        # set up units
        self.set_unit_scaling_factors(length_unit, time_unit)

    def _get_next(self):
        try:
            atoms = next(self._generator_xyz)
        except Exception:
            self._fobj.close()
            self._open = False
            raise StopIteration

        self._atom_types = np.array(list(atoms.symbols))
        self._n_atoms = len(atoms)
        self._cell = atoms.cell[:]
        self._x = atoms.positions
        if 'vel' in atoms.arrays:
            self._v = atoms.arrays['vel']
        else:
            self._v = None

    def __iter__(self):
        return self

    def close(self):
        if not self._fobj.closed:
            self._fobj.close()
            self._open = False

    def __next__(self):
        if not self._open:
            raise StopIteration

        self._get_next()

        if self._v is not None:
            frame = ReaderFrame(frame_index=next(self._frame_index),
                                n_atoms=int(self._n_atoms),
                                cell=self.x_factor * self._cell.copy('F'),
                                positions=self.x_factor * self._x,
                                velocities=self.v_factor * self._v,
                                atom_types=self._atom_types
                                )
        else:
            frame = ReaderFrame(frame_index=next(self._frame_index),
                                n_atoms=int(self._n_atoms),
                                cell=self.x_factor * self._cell.copy('F'),
                                positions=self.x_factor * self._x,
                                atom_types=self._atom_types
                                )
        return frame
