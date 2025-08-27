import os
import pytest
import numpy as np
from dynasor.trajectory import Trajectory
from dynasor.trajectory import WindowIterator
import tempfile


@pytest.fixture
def traj_fname_xtc():
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(
        this_dir,
        'trajectory_reader/trajectory_files/water_10snapshots.xtc')
    return traj_fname


@pytest.fixture
def filenames():
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(this_dir,
                              'trajectory_reader/trajectory_files/dump_long_with_velocities.xyz')
    index_fname = os.path.join(this_dir, 'trajectory_reader/trajectory_files/index_file_dump_long')
    return traj_fname, index_fname


def compare_trajs(traj1, traj2):
    assert len(traj1) == len(traj2)
    for ind, frame1 in enumerate(traj1):
        frame2 = traj2[ind]
        for type in frame1.positions_by_type.keys():
            assert np.allclose(frame1.positions_by_type[type],
                               frame2.positions_by_type[type])
            assert np.allclose(frame1.velocities_by_type[type],
                               frame2.velocities_by_type[type])


def test_traj_step(filenames):
    traj_fname, index_fname = filenames

    # full traj
    step = 1
    trajectory_format = 'extxyz'
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format, frame_step=step)
    traj_full = list(traj)
    assert len(traj_full) == 30
    assert traj.number_of_frames_read == 30

    # every third snapshot
    step = 3
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format, frame_step=step)
    traj_step3 = list(traj)
    assert len(traj_step3) == 10
    assert traj.number_of_frames_read == 10
    compare_trajs(traj_full[::step], traj_step3)


def test_index_file(filenames):
    traj_fname, index_fname = filenames

    n_atoms = 320
    trajectory_format = 'extxyz'

    # atomic_indices is None
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format)
    assert len(traj._atomic_indices) == 1
    assert 'X' in traj._atomic_indices
    assert np.allclose(traj._atomic_indices['X'], np.arange(0, n_atoms, 1))

    # atomic_indices is Dict
    atomic_indices = {'Cs': [0, 1, 2, 3, 4], 'H': [9, 10], 'my group of atoms': [15, 25, 101]}
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format,
                      atomic_indices=atomic_indices)
    assert len(traj._atomic_indices) == 3
    for key in atomic_indices.keys():
        assert np.allclose(traj._atomic_indices[key], atomic_indices[key])

    # From gromacs index-file
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format, atomic_indices=index_fname)
    assert len(traj._atomic_indices) == 3
    assert np.allclose(traj._atomic_indices['Cs'], np.arange(0, 320, 5))
    assert np.allclose(traj._atomic_indices['Pb'], np.arange(1, 320, 5))
    Br_inds = np.array(sorted(list(range(2, 320, 5)) + list(range(3, 320, 5)) + list(range(4, 320, 5)))) # noqa
    assert np.allclose(traj._atomic_indices['Br'], Br_inds)

    # Faulty atomic_indices raises ValueError
    atomic_indices = [1, 2, 3, 4]
    with pytest.raises(ValueError, match=r'Could not understand atomic_indices.'):
        traj = Trajectory(traj_fname, trajectory_format=trajectory_format,
                          atomic_indices=atomic_indices)


def test_filename_property(filenames):
    traj_fname, index_fname = filenames
    traj = Trajectory(traj_fname, trajectory_format='extxyz')
    assert traj.filename == traj_fname


def test_trajectory_with_mdanalysis_reader_xtc(traj_fname_xtc):
    traj = Trajectory(traj_fname_xtc, trajectory_format='xtc')
    frame = next(traj)
    positions = frame.positions_by_type['X']
    assert frame.frame_index == 0
    assert positions.shape == (30, 3)
    assert np.allclose(positions[5], np.array([8.0200005, 12.310001, 28.490002]))


def test_trajectory_file_does_not_exists():
    traj_fname = 'asd'
    with pytest.raises(IOError, match=r'does not exist'):
        Trajectory(traj_fname, trajectory_format='extxyz')


def test_trajectory_with_ambiguous_format(filenames):
    traj_fname, index_fname = filenames

    with pytest.raises(IOError):
        Trajectory(traj_fname, trajectory_format='lammps')


# flake8: noqa: C901
def test_trajectory_repr_html_str(filenames):
    traj_fname, index_fname = filenames
    traj = Trajectory(traj_fname, trajectory_format='extxyz')
    s = traj._repr_html_()
    assert isinstance(s, str)

    s_target_start = """<h3>Trajectory</h3>
<table border="1" class="dataframe">
<thead><tr><th style="text-align: left;">Field</th><th>Value</th></tr></thead>
<tbody>
<tr"><td style="text-align: left;">File name</td><td>"""
    s_target_end = """dump_long_with_velocities.xyz</td></tr>
<tr><td style="text-align: left;">Number of atoms</td><td>320</td></tr>
<tr><td style="text-align: left;">Cell metric</td><td>[[23.77195271  0.          0.        ]
 [ 0.         23.77195271  0.        ]
 [ 0.          0.         23.77195271]]</td></tr>
<tr><td style="text-align: left;">Frame step</td><td>1</td></tr>
<tr><td style="text-align: left;">Atom types</td><td>['X']</td></tr>
</tbody>
</table>"""
    assert s.startswith(s_target_start)
    assert s.endswith(s_target_end)


def test_trajectory_frame_repr_html_str(filenames):
    traj_fname, index_fname = filenames
    traj = Trajectory(traj_fname, trajectory_format='extxyz')
    frame = next(traj)
    s = frame._repr_html_()
    assert isinstance(s, str)
    s_target = """<h3>TrajectoryFrame</h3>
<table border="1" class="dataframe">
<thead><tr><th style="text-align: left;">Field</th><th>Value/Shape</th></tr></thead>
<tbody>
<tr><td style="text-align: left;">Index</td><td>0</td></tr>
<tr><td style="text-align: left;">Positions X</td><td>(320, 3)</td></tr>
<tr><td style="text-align: left;">Velocities X</td><td>(320, 3)</td></tr>
</tbody>
</table>"""
    assert s == s_target


def test_trajectory_with_changing_cell():

    # write dummy file
    s = b"""2
Lattice="4.05 0.0 0.0 0.0 4.05 0.0 0.0 0.0 4.05" Properties=species:S:1:pos:R:3 pbc="T T T"
Al       0.00000000       0.00000000       0.00000000
Al       0.00000000       2.02500000       2.02500000
2
Lattice="4.051 0.0 0.0 0.0 4.05 0.0 0.0 0.0 4.05" Properties=species:S:1:pos:R:3 pbc="T T T"
Al       0.00000000       0.00000000       0.00000000
Al       0.00000000       2.02500000       2.02500000
2
Lattice="4.05 0.0 0.0 0.0 4.05 0.0 0.0 0.0 4.05" Properties=species:S:1:pos:R:3 pbc="T T T"
Al       0.00000000       0.00000000       0.00000000
Al       0.00000000       2.02500000       2.02500000"""
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(s)
    f.seek(0)

    with pytest.raises(ValueError):
        Trajectory(f.name, trajectory_format='extxyz')


def test_windowiterator_stride(filenames):
    traj_fname, index_fname = filenames

    window_size = 4
    max_frames = 12
    trajectory_format = 'extxyz'

    # full traj
    step = 1
    stride = 1
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format,
                      frame_step=step, frame_stop=max_frames)
    window_iterator = WindowIterator(traj, width=window_size, window_step=stride)

    window_indices = []
    for window in window_iterator:
        inds = [frame.frame_index for frame in window]
        window_indices.append(inds)

    window_indices_target = [[0, 1, 2, 3], [1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7],
                             [5, 6, 7, 8], [6, 7, 8, 9], [7, 8, 9, 10], [8, 9, 10, 11],
                             [9, 10, 11], [10, 11], [11]]
    assert window_indices == window_indices_target

    # step > 1
    step = 2
    stride = 1
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format,
                      frame_step=step, frame_stop=max_frames)
    window_iterator = WindowIterator(traj, width=window_size, window_step=stride)

    window_indices = []
    for window in window_iterator:
        inds = [frame.frame_index for frame in window]
        window_indices.append(inds)
    window_indices_target = [[0, 2, 4, 6], [2, 4, 6, 8], [4, 6, 8, 10], [6, 8, 10], [8, 10], [10]]
    assert window_indices == window_indices_target

    # stride > 1
    step = 1
    stride = 2
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format,
                      frame_step=step, frame_stop=max_frames)
    window_iterator = WindowIterator(traj, width=window_size, window_step=stride)

    window_indices = []
    for window in window_iterator:
        inds = [frame.frame_index for frame in window]
        window_indices.append(inds)
    window_indices_target = [[0, 1, 2, 3], [2, 3, 4, 5], [4, 5, 6, 7], [6, 7, 8, 9],
                             [8, 9, 10, 11], [10, 11]]
    assert window_indices == window_indices_target

    # stride > 1 and step > 2
    step = 2
    stride = 2
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format,
                      frame_step=step, frame_stop=max_frames)
    window_iterator = WindowIterator(traj, width=window_size, window_step=stride)

    window_indices = []
    for window in window_iterator:
        inds = [frame.frame_index for frame in window]
        window_indices.append(inds)
    window_indices_target = [[0, 2, 4, 6], [4, 6, 8, 10], [8, 10]]
    assert window_indices == window_indices_target


def test_large_window_step(filenames):
    # test when window step is larger than window size

    traj_fname, index_fname = filenames
    max_frames = 20
    frame_step = 1
    window_size = 5
    window_step = 7
    trajectory_format = 'extxyz'
    traj = Trajectory(traj_fname, trajectory_format=trajectory_format,
                      frame_step=frame_step, frame_stop=max_frames)
    window_iterator = WindowIterator(traj, width=window_size, window_step=window_step)

    window_indices = []
    for window in window_iterator:
        inds = [frame.frame_index for frame in window]
        window_indices.append(inds)
    window_indices_target = [[0, 1, 2, 3, 4], [7, 8, 9, 10, 11], [14, 15, 16, 17, 18]]
    assert window_indices == window_indices_target


def test_invalid_inputs_to_trajectory(filenames):
    traj_fname, index_fname = filenames
    trajectory_format = 'extxyz'

    frame_step = -1
    with pytest.raises(ValueError, match=r'frame_step should be positive'):
        Trajectory(traj_fname, trajectory_format=trajectory_format, frame_step=frame_step)

    frame_start = -1
    with pytest.raises(ValueError, match=r'frame_start should be positive'):
        Trajectory(traj_fname, trajectory_format=trajectory_format, frame_start=frame_start)

    # max of atomic indices exceeds number of atoms
    atomic_indices = dict()
    atomic_indices['Cs'] = [1, 2, 3, 4, 1100]
    with pytest.raises(ValueError, match=r'index in atomic_indices exceeds number of atoms'):
        Trajectory(traj_fname, trajectory_format=trajectory_format, atomic_indices=atomic_indices)

    # negative index in atomic indices
    atomic_indices = dict()
    atomic_indices['Cs'] = [1, 2, 3, -4, 5]
    with pytest.raises(ValueError, match=r'minimum index in atomic_indices is negative'):
        Trajectory(traj_fname, trajectory_format=trajectory_format, atomic_indices=atomic_indices)

    # negative index in atomic indices
    atomic_indices = dict()
    atomic_indices['Cs'] = [1, 2, 3, 4, 5]
    atomic_indices['Cs_and_Pb'] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    with pytest.raises(ValueError, match=r'The char "_" is not allowed in atomic_indices.'):
        Trajectory(traj_fname, trajectory_format=trajectory_format, atomic_indices=atomic_indices)
