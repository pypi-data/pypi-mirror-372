import numpy as np
import os
import pytest
import tempfile
from dynasor.trajectory.atomic_indices import parse_gromacs_index_file


@pytest.fixture
def index_fname():
    this_dir = os.path.dirname(__file__)
    index_fname = os.path.join(this_dir, 'trajectory_reader/trajectory_files/index_file_dump_long')
    return index_fname


def test_parse_gromacs_index_file(index_fname):
    atomic_indices = parse_gromacs_index_file(index_fname)
    Br_inds = np.array(sorted(list(range(2, 320, 5)) + list(range(3, 320, 5)) + list(range(4, 320, 5)))) # noqa
    assert sorted(atomic_indices) == ['Br', 'Cs', 'Pb']
    assert np.allclose(atomic_indices['Cs'], np.arange(0, 320, 5))
    assert np.allclose(atomic_indices['Pb'], np.arange(1, 320, 5))
    assert np.allclose(atomic_indices['Br'], Br_inds)


def test_raise_file_does_not_exists():
    fname = 'asd'
    with pytest.raises(ValueError):
        parse_gromacs_index_file(fname)


def test_duplicate_groups_in_indexfile():

    # write dummy file with duplicate Cs group
    s = b"""[ Cs ]
    1  6  11  16
    [ Pb ]
    2  7  12  17
    [ Br ]
    3  4  5
    [ Cs ]
    101  106  111 116
    """
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(s)
    f.seek(0)

    atomic_indices = parse_gromacs_index_file(f.name)
    assert atomic_indices['Cs'].tolist() == [100, 105, 110, 115]
    assert atomic_indices['Pb'].tolist() == [1, 6, 11, 16]
    assert atomic_indices['Br'].tolist() == [2, 3, 4]
