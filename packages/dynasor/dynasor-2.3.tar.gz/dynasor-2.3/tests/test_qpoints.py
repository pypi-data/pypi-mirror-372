import numpy as np
import pytest
from dynasor.qpoints import get_spherical_qpoints, get_supercell_qpoints_along_path
from ase.build import bulk


def test_get_spherical_qpoints():

    cell = np.diag([2.2, 3.76, 4.01])
    q_max = 20

    # without pruning
    q_points = get_spherical_qpoints(cell, q_max)
    assert q_points.shape[0] == 4465
    assert q_points.shape[1] == 3
    assert np.max(np.linalg.norm(q_points, axis=1)) <= q_max

    # with pruning
    max_points = 250
    q_points = get_spherical_qpoints(cell, q_max, max_points=max_points)

    assert q_points.shape[0] < max_points + 100
    assert q_points.shape[1] == 3
    assert np.max(np.linalg.norm(q_points, axis=1)) <= q_max


def test_get_spherical_qpoints_with_seed():
    cell = np.diag([2.2, 3.76, 4.01])
    q_max = 30
    max_points = 1500
    q_points1 = get_spherical_qpoints(cell, q_max, max_points=max_points, seed=42)
    q_points2 = get_spherical_qpoints(cell, q_max, max_points=max_points, seed=43)
    q_points3 = get_spherical_qpoints(cell, q_max, max_points=max_points, seed=42)
    assert np.allclose(q_points1, q_points3)
    assert q_points1.shape != q_points2.shape


def test_get_spherical_qpoints_values():
    cell = np.diag([2.2, 3.76, 4.01])
    q_max = 10
    max_points = 20
    target = [[-5.71198664,  0,          -3.13375826],
              [-2.85599332, -6.68423969,  4.70063739],
              [-2.85599332, -3.34211984, -1.56687913],
              [-2.85599332,  0,          -4.70063739],
              [-2.85599332,  0,           0],
              [-2.85599332,  5.01317977, -3.13375826],
              [-2.85599332,  5.01317977,  1.56687913],
              [0,           -6.68423969, -1.56687913],
              [0,           -5.01317977, -6.26751652],
              [0,            0,          -1.56687913],
              [0,            0,           0],
              [0,            0,           6.26751652],
              [0,            1.67105992,  0],
              [0,            1.67105992,  1.56687913],
              [0,            3.34211984, -1.56687913],
              [0,            3.34211984,  0],
              [0,            6.68423969, -3.13375826],
              [2.85599332,  -3.34211984,  1.56687913],
              [2.85599332,   0,          -1.56687913],
              [2.85599332,   0,           9.40127477],
              [2.85599332,   8.35529961,  3.13375826],
              [5.71198664,  -5.01317977,  3.13375826],
              [8.56797996,   1.67105992,  0]]
    actual = get_spherical_qpoints(cell, q_max, max_points=max_points, seed=42)
    assert np.allclose(actual, target)


def test_get_supercell_qpts_along_path_cubic():
    prim = bulk('Al', 'fcc', a=4.05)
    supercell = bulk('Al', 'fcc', a=4.05, cubic=True).repeat(4)
    coordinates = dict(
        X=[0.5, 0.5, 0],
        G=[0, 0, 0],
        L=[0.5, 0.5, 0.5],
        W=[0.5, 0.25, 0.75],
    )

    # connected path
    path = [('X', 'G'), ('G', 'L')]
    qpoints = get_supercell_qpoints_along_path(path, coordinates, prim.cell, supercell.cell)
    assert len(qpoints) == len(path)

    qpoints_target = [
        np.array([[0,          0,          1.55140378],
                  [0,          0,          1.16355283],
                  [0,          0,          0.77570189],
                  [0,          0,          0.38785094],
                  [0,          0,          0]]),
        np.array([[0,          0,          0],
                  [0.38785094, 0.38785094, 0.38785094],
                  [0.77570189, 0.77570189, 0.77570189]])
        ]

    assert len(qpoints) == len(qpoints_target)
    for q_segment1, q_segment2 in zip(qpoints, qpoints_target):
        assert np.allclose(q_segment1, q_segment2)

    # disconnected path
    path = [('X', 'G'), ('G', 'L'), ('W', 'X')]
    qpoints = get_supercell_qpoints_along_path(path, coordinates, prim.cell, supercell.cell)
    assert len(qpoints) == len(path)

    qpoints_target = [
        np.array([[0,          0,          1.55140378],
                  [0,          0,          1.16355283],
                  [0,          0,          0.77570189],
                  [0,          0,          0.38785094],
                  [0,          0,          0]]),
        np.array([[0,          0,          0],
                  [0.38785094, 0.38785094, 0.38785094],
                  [0.77570189, 0.77570189, 0.77570189]]),
        np.array([[0.77570189, 1.55140378, 0],
                  [0.38785094, 0.77570189, 0.77570189],
                  [0, 0, 1.55140378]])
        ]

    assert len(qpoints) == len(qpoints_target)
    for q_segment1, q_segment2 in zip(qpoints, qpoints_target):
        assert np.allclose(q_segment1, q_segment2)


def test_get_supercell_qpts_along_path_hex():
    prim = bulk('Al', 'hcp', a=3.05, c=5.0)
    supercell = prim.repeat(4)
    coordinates = dict(
        X=[0.5, 0.5, 0],
        G=[0, 0, 0],
        L=[0.5, 0.5, 0.5],
        W=[0.5, 0.25, 0.75],
    )

    # connected path
    path = [('X', 'G'), ('G', 'L')]
    qpoints = get_supercell_qpoints_along_path(path, coordinates, prim.cell, supercell.cell)
    assert len(qpoints) == len(path)

    qpoints_target = [
        np.array([[1.03003038, 1.78406495, 0],
                  [0.51501519, 0.89203247, 0],
                  [0, 0, 0]]),
        np.array([[0, 0, 0],
                  [0.51501519, 0.89203247, 0.31415927],
                  [1.03003038, 1.78406495, 0.62831853]]),
        ]
    assert len(qpoints) == len(qpoints_target)
    for q_segment1, q_segment2 in zip(qpoints, qpoints_target):
        assert np.allclose(q_segment1, q_segment2)


def test_get_supercell_qpoints_along_path():
    prim = bulk('Al', 'fcc', a=4.0)
    supercell = bulk('Al', 'fcc', a=4.0, cubic=True).repeat(1)
    path = [('X', 'G'), ('A', 'B'), ('G', 'L')]
    coordinates = dict(X=[0.5, 0.5, 0], G=[0, 0, 0], L=[0.5, 0.5, 0.5], A=[1/6, 1/6, 1/6],
                       B=[2/6, 2/6, 2/6])
    with pytest.warns(UserWarning, match='No q-points along path!'):
        qpoints = get_supercell_qpoints_along_path(path, coordinates, prim.cell, supercell.cell)
    assert len(qpoints) == 3
    assert qpoints[1].shape == (0, 3)


def test_get_supercell_qpts_along_path_errors():
    prim = bulk('Al', 'fcc', a=4.0)
    supercell = bulk('Al', 'fcc', a=4.05, cubic=True).repeat(4)
    path = [('X', 'G'), ('G', 'L')]
    coordinates = dict(X=[0.5, 0.5, 0], G=[0, 0, 0], L=[0.5, 0.5, 0.5])
    with pytest.raises(ValueError, match='Please check that the supercell metric'):
        qpoints, labels = get_supercell_qpoints_along_path(
            path, coordinates, prim.cell, supercell.cell)

    coordinates = dict(X=[0.5, 0.5, 0], G=[0, 0, 0])
    with pytest.raises(ValueError, match='Please check that the supercell metric'):
        qpoints, labels = get_supercell_qpoints_along_path(
            path, coordinates, prim.cell, supercell.cell)
