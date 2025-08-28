"""Wrapper utility functions for tetrahedron meshes, implemented in C++."""

from distmeshpy._typing import Array, Triangulation

from ._tetrahedron_utils import (
    _tetrahedron_find_edges,
    _tetrahedron_find_surface,
)


def tetrahedron_find_edges(f2v: Triangulation) -> Triangulation:
    """
    Find edges of a tetrahedron mesh.

    :param f2v: (Ne, 4) The tetrahedron mesh.
    :type f2v: Triangulation
    :return: The edges of the tetrahedron mesh.
    :rtype: Triangulation
    """
    return _tetrahedron_find_edges(f2v)


def tetrahedron_find_surface(pts: Array, f2v: Triangulation) -> Triangulation:
    """
    Find the surface of a tetrahedron mesh.

    :param pts: (N, 3) The vertex coordinates of the tetrahedron mesh.
    :type pts: Array
    :param f2v: (Ne, 4) The tetrahedron mesh.
    :type f2v: Triangulation
    :return: The surface of the tetrahedron mesh.
    :rtype: Triangulation
    """
    return _tetrahedron_find_surface(pts, f2v)
