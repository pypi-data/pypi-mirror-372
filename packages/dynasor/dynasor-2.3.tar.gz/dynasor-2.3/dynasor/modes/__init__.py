"""
The mode projection functionality in dynasor is mainly handled by two objects:
The :class:`~dynasor.ModeProjector` class and :func:`~dynasor.project_modes`
function.  The :class:`~dynasor.ModeProjector` provides access to
data objects representing a q-point :attr:`~dynasor.modes.qpoint.QPoint` and
from the q-point there is access to an object representing a particular band
:class:`~dynasor.modes.band.Band` at that q-point.  In addition, simple wrappers
around the coordinates `Q`, `P` and `F` exist via
:class:`~dynasor.modes.complex_coordinate.ComplexCoordinate` to easily set the
amplitude and phase of a mode while preserving the :math:`Q(-q)=Q^*(q)`
symmetries.  Internally dynasor wraps the primitive cell
:class:`~dynasor.modes.atoms.Prim` and supercell
:class:`~dynasor.modes.atoms.Supercell`.  As a user only the
:class:`~dynasor.ModeProjector` and :attr:`~dynasor.project_modes` should need
to be imported.
"""
