#ifndef TETRAHEDRON_UTILS_HPP
#define TETRAHEDRON_UTILS_HPP

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

py::array_t<int> _tetrahedron_find_edges(py::array_t<int>);

py::array_t<int> _tetrahedron_find_surface(py::array_t<double>, py::array_t<int>);

#endif  // !TETRAHEDRON_UTILS_HPP