"""Wrapper utility functions for triangular meshes, implemented in C++."""

from distmeshpy._typing import Array, Float, Triangulation

from ._triangle_utils import (
    _triangle_area,
    _triangle_area_all,
    _triangle_find_edges,
    _triangle_normal,
    _triangle_normal_all,
    _triangle_quality,
    _triangle_quality_all,
    _TriangleConnectivity,
)


def triangle_area(p1: Array, p2: Array, p3: Array) -> Float:
    """
    Find the area of a triangle in 3D space.

    :param p1: (3, ) First vertex.
    :type p1: Array
    :param p2: (3, ) Second vertex.
    :type p2: Array
    :param p3: (3, ) Third vertex.
    :type p3: Array
    :return: Area of the triangle
    :rtype: Float
    """
    return _triangle_area(p1, p2, p3)


def triangle_area_all(p1: Array, p2: Array, p3: Array) -> Array:
    """
    Find the area of all triangle in 3D space defined by each row of the input arrays.

    :param p1: (N, 3) First vertices.
    :type p1: Array
    :param p2: (N, 3) Second vertices.
    :type p2: Array
    :param p3: (N, 3) Third vertices.
    :type p3: Array
    :return: (N, ) Areas of the triangle
    :rtype: Array
    """
    return _triangle_area_all(p1, p2, p3)


def triangle_normal(p1: Array, p2: Array, p3: Array) -> Array:
    """
    Find the unit normal vector of a triangle in 3D space.

    The employed convention assumes counter-clockwise vertex indexing.
    Hence, the normal vector is the normalized (p2 - p1) x (p3 - p1).

    :param p1: (3, ) First vertex.
    :type p1: Array
    :param p2: (3, ) Second vertex.
    :type p2: Array
    :param p3: (3, ) Third vertex.
    :type p3: Array
    :return: (3, ) Normal vector of the triangle.
    :rtype: Array
    """
    return _triangle_normal(p1, p2, p3)


def triangle_normal_all(p1: Array, p2: Array, p3: Array) -> Array:
    """
    Find the unit normal vector of all input triangles in 3D space.

    The employed convention assumes counter-clockwise vertex indexing.
    Hence, the normal vector is the normalized (p2 - p1) x (p3 - p1).

    :param p1: (N, 3) First vertices.
    :type p1: Array
    :param p2: (N, 3) Second vertices.
    :type p2: Array
    :param p3: (N, 3) Third vertices.
    :type p3: Array
    :return: (N, 3) Normal vectors of given triangles triangle.
    :rtype: Array
    """
    return _triangle_normal_all(p1, p2, p3)


def triangle_quality(p1: Array, p2: Array, p3: Array) -> Float:
    """
    Find the mesh quality of a triangle in 3D space.

    :param p1: (3, ) First vertex.
    :type p1: Array
    :param p2: (3, ) Second vertex.
    :type p2: Array
    :param p3: (3, ) Third vertex.
    :type p3: Array
    :return: Quality of the triangle
    :rtype: Float
    """
    return _triangle_quality(p1, p2, p3)


def triangle_quality_all(p1: Array, p2: Array, p3: Array) -> Array:
    """
    Find the mesh quality of all input triangles in 3D space.

    :param p1: (N, 3) First vertices.
    :type p1: Array
    :param p2: (N, 3) Second vertices.
    :type p2: Array
    :param p3: (N, 3) Third vertices.
    :type p3: Array
    :return: (N, ) Qualities of all input triangles.
    :rtype: Array
    """
    return _triangle_quality_all(p1, p2, p3)


def triangle_find_edges(f2v: Triangulation) -> Triangulation:
    """
    Find all edges of a triangular mesh.

    :param p1: (Ne, 3) The triangular mesh.
    :type p1: Triangulation
    :return: (N, 2) Edges of the mesh.
    :rtype: Float
    """
    return _triangle_find_edges(f2v)


class TriangleConnectivity(_TriangleConnectivity):
    """An auxiliary class to handle the connectivity of a triangular mesh."""

    def __init__(self, f2v: Triangulation) -> None:
        """
        Initialize a TriangleConnectivity object.

        A triangular mesh is required to initialize a Triangulation object.
        The mesh is processed to find all shared edges along with the connecting
        triangles. After initialization, the f2v object should not be modified
        in between calls to the update_connectivity method, as the internally
        stored connectivity information may become invalid.

        This class is used internally by the distmesh2d and
        distmeshsurface functions. Typically, users should not find the need to
        use this class directly.

        :param f2v: Input triangular mesh.
        :type f2v: Triangulation
        """
        super().__init__(f2v)

    def update_connectivity(self, points: Array, f2v: Triangulation) -> None:
        """
        Evaluate the quality of meshes and attempt to improve them via edge flipping.

        This functionality of this method mirrors that of "trisurfupd" in the original
        MATLAB implementation.

        :param points: Nodal coordinates of the mesh.
        :type points: Array
        :param f2v: The triangular mesh.
        :type f2v: Triangulation
        """
        self._update_connectivity(points, f2v)
