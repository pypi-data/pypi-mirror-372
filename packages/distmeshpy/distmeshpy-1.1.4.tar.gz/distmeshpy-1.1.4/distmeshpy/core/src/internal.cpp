#include "internal.hpp"

#include <cmath>

void _apply_force_2d(py::array_t<double> force_on_bar,
                     py::array_t<double> force_vector,
                     py::array_t<int> bar_index) {
    auto force_on_bar_ = force_on_bar.mutable_unchecked<2>();
    auto force_vector_ = force_vector.unchecked<2>();
    auto bar_index_ = bar_index.unchecked<2>();

    for (ssize_t i = 0; i < bar_index_.shape(0); ++i) {
        force_on_bar_(bar_index_(i, 0), 0) += force_vector_(i, 0);
        force_on_bar_(bar_index_(i, 0), 1) += force_vector_(i, 1);

        force_on_bar_(bar_index_(i, 1), 0) -= force_vector_(i, 0);
        force_on_bar_(bar_index_(i, 1), 1) -= force_vector_(i, 1);
    }
}

void _apply_force_3d(py::array_t<double> force_on_bar,
                     py::array_t<double> force_vector,
                     py::array_t<int> bar_index) {
    auto force_on_bar_ = force_on_bar.mutable_unchecked<2>();
    auto force_vector_ = force_vector.unchecked<2>();
    auto bar_index_ = bar_index.unchecked<2>();

    for (ssize_t i = 0; i < bar_index_.shape(0); ++i) {
        force_on_bar_(bar_index_(i, 0), 0) += force_vector_(i, 0);
        force_on_bar_(bar_index_(i, 0), 1) += force_vector_(i, 1);
        force_on_bar_(bar_index_(i, 0), 2) += force_vector_(i, 2);

        force_on_bar_(bar_index_(i, 1), 0) -= force_vector_(i, 0);
        force_on_bar_(bar_index_(i, 1), 1) -= force_vector_(i, 1);
        force_on_bar_(bar_index_(i, 1), 2) -= force_vector_(i, 2);
    }
}

PYBIND11_MODULE(_internal, m) { 
    m.def("_apply_force_2d", &_apply_force_2d); 
    m.def("_apply_force_3d", &_apply_force_3d);
}
