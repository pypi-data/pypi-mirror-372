#ifndef FORCE_HPP
#define FORCE_HPP

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

void _apply_force_2d(py::array_t<double>, py::array_t<double>, py::array_t<int>);
void _apply_force_3d(py::array_t<double>, py::array_t<double>, py::array_t<int>);

#endif  // FORCE_HPP