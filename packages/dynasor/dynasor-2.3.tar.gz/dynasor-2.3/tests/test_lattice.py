import numpy as np
from dynasor.qpoints.lattice import Lattice
import pytest


def test_lattice():

    tests = 0
    while tests < 100:
        prim = np.random.uniform(-5, 5, size=(3, 3))

        P = np.random.randint(-5, 5, size=(3, 3))
        if np.abs(np.linalg.det(P)) < 1:
            continue

        supercell = P @ prim

        lat = Lattice(prim, supercell)

        assert np.allclose(lat.P, P)

        qpoints = np.random.normal(size=(100, 3))

        red = lat.cartesian_to_reduced(qpoints)
        cart = lat.reduced_to_cartesian(red)

        assert np.allclose(cart, qpoints)

        paths = 0
        while paths < 20:
            start = np.random.randint(-5, 5, size=3) @ lat.reciprocal_supercell
            stop = np.random.randint(-5, 5, size=3) @ lat.reciprocal_supercell
            start_red = lat.cartesian_to_reduced(start)
            stop_red = lat.cartesian_to_reduced(stop)
            points, dists = lat.make_path(start_red, stop_red)

            assert np.allclose(points[0], start)
            assert np.allclose(points[-1], stop)

            if len(points) < 3:
                continue

            for p in points[1:-1]:
                n = np.linalg.solve(lat.reciprocal_supercell.T, p)
                assert np.allclose(n, n.round(0))
            paths += 1

        tests += 1


def test_make_path():

    q1, q2 = [0.5, 0.0, 0.0], [0.5, 0.5, 0.0]

    prim = np.array([[4, 0, 0], [0, 4, 0], [0, 0, 4]])

    repeat = 4  # works
    supercell = prim * repeat
    lat = Lattice(prim, supercell)

    qpts, dists = lat.make_path(q1, q2)

    assert np.allclose(
            (qpts/(2*np.pi)).flat,
            [1/8, 0, 0, 1/8, 1/16, 0, 1/8, 1/8, 0]
            )
    assert np.allclose(dists, [0, 1/2, 1])

    repeat = 5  # fails
    supercell = prim * repeat
    lat = Lattice(prim, supercell)

    with pytest.warns(UserWarning, match='No q-points along path!'):
        qpts, dists = lat.make_path(q1, q2)

    assert qpts.shape == (0, 3)
    assert dists.shape == (0,)
