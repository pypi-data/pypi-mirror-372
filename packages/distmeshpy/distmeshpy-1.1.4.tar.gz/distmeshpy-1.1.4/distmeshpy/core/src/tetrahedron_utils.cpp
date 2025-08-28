#include "tetrahedron_utils.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <map>
#include <unordered_set>
#include <utility>

#include "helpers.hpp"
#include "triangle_utils.hpp"

namespace py = pybind11;

namespace {
using pair_t = typename std::pair<unsigned int, unsigned int>;
using f_array_t = typename py::array_t<double>;
using i_array_t = typename py::array_t<int>;

// Face indices correspond to that of the opposite vertex
// Orientation follows the right-hand rule with outward normals
std::array<int, 4> face_idx1{1, 2, 3, 0};
std::array<int, 4> face_idx2{3, 3, 1, 1};
std::array<int, 4> face_idx3{2, 0, 0, 2};

// Six edges in no particular order
std::array<int, 6> edge_idx1{0, 1, 2, 3, 3, 3};
std::array<int, 6> edge_idx2{1, 2, 0, 0, 1, 2};
}  // namespace

i_array_t _tetrahedron_find_edges(i_array_t f2v) {
    auto f2v_ = f2v.unchecked<2>();
    std::unordered_set<pair_t, pair_hash> edge_set;
    for (int i = 0; i < f2v_.shape(0); ++i) {
        for (int j = 0; j < 6; ++j) {
            unsigned n1 = f2v_(i, edge_idx1[j]);
            unsigned n2 = f2v_(i, edge_idx2[j]);
            auto e_curr =
                n1 < n2 ? std::make_pair(n1, n2) : std::make_pair(n2, n1);
            edge_set.insert(e_curr);
        }
    }

    i_array_t edges({static_cast<py::ssize_t>(edge_set.size()),
                     static_cast<py::ssize_t>(2)});
    auto edges_ = edges.mutable_unchecked<2>();
    ssize_t i = 0;
    for (auto it = edge_set.begin(); it != edge_set.end(); ++it) {
        edges_(i, 0) = it->first;
        edges_(i, 1) = it->second;
        i++;
    }
    return edges;
}

i_array_t _tetrahedron_find_surface(f_array_t pos, i_array_t f2v) {
    auto f2v_ = f2v.unchecked<2>();
    auto pos_ = pos.unchecked<2>();
    std::map<std::array<int, 3>, pair_t> face_map;
    for (int i = 0; i < f2v_.shape(0); ++i) {
        for (int j = 0; j < 4; ++j) {
            std::array<int, 3> face{f2v_(i, face_idx1[j]),
                                    f2v_(i, face_idx2[j]),
                                    f2v_(i, face_idx3[j])};
            std::sort(face.begin(), face.end());
            auto it = face_map.find(face);
            if (it == face_map.end()) {
                face_map[face] = std::make_pair(i, j);
            } else {
                face_map.erase(it);
            }
        }
    }

    i_array_t faces({static_cast<py::ssize_t>(face_map.size()),
                     static_cast<py::ssize_t>(3)});
    auto faces_ = faces.mutable_unchecked<2>();
    int k = 0;
    for (auto item : face_map) {
        std::array<int, 3> face = item.first;
        int i = item.second.first;
        int j = item.second.second;
        f_array_t normal = _triangle_normal(
            py::cast<f_array_t>(
                pos[py::make_tuple(face[0], py::ellipsis())]),
            py::cast<f_array_t>(
                pos[py::make_tuple(face[1], py::ellipsis())]),
            py::cast<f_array_t>(
                pos[py::make_tuple(face[2], py::ellipsis())]));
        auto normal_ = normal.unchecked<1>();
        double dot_prod = dot(normal_[0], normal_[1], normal_[2],
                              pos_(f2v_(i, j), 0) - pos_(face[0], 0),
                              pos_(f2v_(i, j), 1) - pos_(face[0], 1),
                              pos_(f2v_(i, j), 2) - pos_(face[0], 2));
        if (std::abs(dot_prod) < 1e-10) {
            throw std::runtime_error("Degenerate element");
        } else if (dot_prod < 0) {
            faces_(k, 0) = face[0];
            faces_(k, 1) = face[1];
            faces_(k, 2) = face[2];
        } else {
            faces_(k, 0) = face[2];
            faces_(k, 1) = face[1];
            faces_(k, 2) = face[0];
        }
        k++;
    }
    return faces;
}

PYBIND11_MODULE(_tetrahedron_utils, m) {
    m.def("_tetrahedron_find_edges", &_tetrahedron_find_edges);
    m.def("_tetrahedron_find_surface", &_tetrahedron_find_surface);
}