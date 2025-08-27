import os
import pytest
import numpy as np
from tempfile import NamedTemporaryFile
from dynasor.trajectory import Trajectory
from dynasor.qpoints import get_spherical_qpoints
from dynasor.correlation_functions import compute_dynamic_structure_factors
from dynasor.post_processing import get_spherically_averaged_sample_binned
from dynasor.sample import read_sample_from_npz


@pytest.fixture
def filenames():
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(this_dir,
                              'trajectory_reader/trajectory_files/dump_long_with_velocities.xyz')
    index_fname = os.path.join(this_dir, 'trajectory_reader/trajectory_files/index_file_dump_long')
    return traj_fname, index_fname


def test_dynasor_CLI(filenames):
    # input parameters
    time_window = 8
    max_frames = 100000
    dt = 100

    q_max = 40
    q_bins = 20
    max_q_points = 10000

    traj_fname, index_fname = filenames

    tmpfile = NamedTemporaryFile(suffix='.npz', delete=False)

    # setup dynasor command
    flags = []
    flags.append(f'-f {traj_fname} -n {index_fname}')
    flags.append('--trajectory-format=extxyz')

    flags.append(f'--q-bins={q_bins}')
    flags.append(f'--q-max={q_max}')
    flags.append(f'--max-q-points={max_q_points}')

    flags.append(f'--time-window={time_window}')
    flags.append(f'--dt={dt}')
    flags.append(f'--max-frames={max_frames}')

    flags.append(f'--outfile={tmpfile.name}')
    flags.append('--calculate-incoherent')
    flags.append('--calculate-currents')

    flags_str = ' '.join(flags)

    # Run dynasor and read results
    command = 'dynasor ' + flags_str
    os.system(command)

    sample_cli = read_sample_from_npz(tmpfile.name)

    # Compute results with dynasor API
    traj = Trajectory(traj_fname, trajectory_format='extxyz', atomic_indices=index_fname)
    q_points = get_spherical_qpoints(traj.cell, q_max=q_max, max_points=max_q_points)
    sample = compute_dynamic_structure_factors(traj, q_points, dt=dt, window_size=time_window,
                                               calculate_currents=True, calculate_incoherent=True)
    sample_api = get_spherically_averaged_sample_binned(sample, num_q_bins=q_bins)

    # compare results
    assert np.allclose(sample_api.time, sample_cli.time)
    assert np.allclose(sample_api.omega, sample_cli.omega)
    assert np.allclose(sample_api.q_norms, sample_cli.q_norms)
    for key in sample_api.available_correlation_functions:
        assert np.allclose(getattr(sample_api, key), getattr(sample_cli, key))
