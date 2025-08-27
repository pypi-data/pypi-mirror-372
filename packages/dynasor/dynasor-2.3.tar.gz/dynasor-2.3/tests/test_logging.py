import os
import pytest
from io import StringIO
import logging
from dynasor.logging_tools import logger, set_logging_level
from dynasor.trajectory import Trajectory


@pytest.fixture
def traj_fname_xyz():
    this_dir = os.path.dirname(__file__)
    traj_fname = os.path.join(this_dir,
                              'trajectory_reader/trajectory_files/dump_with_velocities.xyz')
    return traj_fname


def test_set_logging_level(traj_fname_xyz):

    # Log Trajectory output to StringIO stream
    for handler in logger.handlers:
        logger.removeHandler(handler)
    stream = StringIO()
    stream_handler = logging.StreamHandler(stream)
    logger.addHandler(stream_handler)
    Trajectory(traj_fname_xyz, 'extxyz')

    lines1 = stream.getvalue().split('\n')[:-1]  # remove last blank line
    assert 'Trajectory file:' in lines1[2]
    assert 'Total number of particles: 1080' in lines1[3]

    # rerun with lower vebosity
    set_logging_level('ERROR')
    for handler in logger.handlers:
        logger.removeHandler(handler)
    stream = StringIO()
    stream_handler = logging.StreamHandler(stream)
    logger.addHandler(stream_handler)
    Trajectory(traj_fname_xyz, 'extxyz')

    lines2 = stream.getvalue().split('\n')[:-1]  # remove last blank line
    assert lines2 == []
