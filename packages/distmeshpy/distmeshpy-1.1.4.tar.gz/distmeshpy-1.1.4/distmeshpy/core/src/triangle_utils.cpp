#include "triangle_utils.hpp"

#include <algorithm>
#include <cmath>
#include <unordered_map>
#include <unordered_set>
#include <utility>  // std::pair

#include "helpers.hpp"

namespace {
using pair_t = typename std::pair<unsigned int, unsigned int>;
using f_array_t = typename py::array_t<double>;
using i_array_t = typename py::array_t<int>;
std::array<int, 3> idx1{1, 2, 0};
std::array<int, 3> idx2{2, 0, 1};
}  // namespace

double _triangle_area(f_array_t p1, f_array_t p2, f_array_t p3) {
    // Assume inputs are 1D vectors of length 3
    auto pt1 = p1.unchecked<1>();
    auto pt2 = p2.unchecked<1>();
    auto pt3 = p3.unchecked<1>();

    std::array<double, 3> u{pt2(0) - pt1(0), pt2(1) - pt1(1), pt2(2) - pt1(2)};
    std::array<double, 3> v{pt3(0) - pt1(0), pt3(1) - pt1(1), pt3(2) - pt1(2)};
    auto n = cross(u[0], u[1], u[2], v[0], v[1], v[2]);
    return 0.5 * norm(n[0], n[1], n[2]);
}

f_array_t _triangle_area_all(f_array_t p1, f_array_t p2, f_array_t p3) {
    auto pts1 = p1.unchecked<2>();
    auto pts2 = p2.unchecked<2>();
    auto pts3 = p3.unchecked<2>();

    ssize_t n = pts1.shape(0);
    f_array_t areas(n);
    auto area = areas.mutable_unchecked<1>();
    double u1, u2, u3, v1, v2, v3;

    for (ssize_t i = 0; i < n; ++i) {
        u1 = pts2(i, 0) - pts1(i, 0);
        u2 = pts2(i, 1) - pts1(i, 1);
        u3 = pts2(i, 2) - pts1(i, 2);
        v1 = pts3(i, 0) - pts1(i, 0);
        v2 = pts3(i, 1) - pts1(i, 1);
        v3 = pts3(i, 2) - pts1(i, 2);
        auto n = cross(u1, u2, u3, v1, v2, v3);
        area(i) = 0.5 * norm(n[0], n[1], n[2]);
    }
    return areas;
}

f_array_t _triangle_normal(f_array_t p1, f_array_t p2, f_array_t p3) {
    // Assume inputs are 1D vectors of length 3
    auto pt1 = p1.unchecked<1>();
    auto pt2 = p2.unchecked<1>();
    auto pt3 = p3.unchecked<1>();

    std::array<double, 3> u{pt2(0) - pt1(0), pt2(1) - pt1(1), pt2(2) - pt1(2)};
    std::array<double, 3> v{pt3(0) - pt1(0), pt3(1) - pt1(1), pt3(2) - pt1(2)};
    auto n = cross(u[0], u[1], u[2], v[0], v[1], v[2]);
    double n_norm = norm(n[0], n[1], n[2]);
    n[0] /= n_norm;
    n[1] /= n_norm;
    n[2] /= n_norm;

    return f_array_t(3, n.data());
}

f_array_t _triangle_normal_all(f_array_t p1, f_array_t p2, f_array_t p3) {
    py::buffer_info buf = p1.request();
    auto normals = f_array_t(buf);
    auto pts1 = p1.unchecked<2>();
    auto pts2 = p2.unchecked<2>();
    auto pts3 = p3.unchecked<2>();

    auto normal = normals.mutable_unchecked<2>();
    double u1, u2, u3, v1, v2, v3;

    ssize_t n = pts1.shape(0);
    for (ssize_t i = 0; i < n; ++i) {
        u1 = pts2(i, 0) - pts1(i, 0);
        u2 = pts2(i, 1) - pts1(i, 1);
        u3 = pts2(i, 2) - pts1(i, 2);
        v1 = pts3(i, 0) - pts1(i, 0);
        v2 = pts3(i, 1) - pts1(i, 1);
        v3 = pts3(i, 2) - pts1(i, 2);
        auto n = cross(u1, u2, u3, v1, v2, v3);
        auto n_norm = norm(n[0], n[1], n[2]);
        normal(i, 0) = n[0] / n_norm;
        normal(i, 1) = n[1] / n_norm;
        normal(i, 2) = n[2] / n_norm;
    }

    return normals;
}

double _triangle_quality(f_array_t p1, f_array_t p2, f_array_t p3) {
    // Assume inputs are 1D vectors of length 3
    auto pt1 = p1.unchecked<1>();
    auto pt2 = p2.unchecked<1>();
    auto pt3 = p3.unchecked<1>();

    std::array<double, 3> d12{pt2(0) - pt1(0), pt2(1) - pt1(1),
                              pt2(2) - pt1(2)};
    std::array<double, 3> d13{pt3(0) - pt1(0), pt3(1) - pt1(1),
                              pt3(2) - pt1(2)};
    std::array<double, 3> d23{pt3(0) - pt2(0), pt3(1) - pt2(1),
                              pt3(2) - pt2(2)};
    auto n = cross(d12[0], d12[1], d12[2], d13[0], d13[1], d13[2]);
    double vol = 0.5 * norm(n[0], n[1], n[2]);
    double den = norm_sq(d12[0], d12[1], d12[2]) +
                 norm_sq(d13[0], d13[1], d13[2]) +
                 norm_sq(d23[0], d23[1], d23[2]);
    return 6.928203230275509 * vol / den;
}

f_array_t _triangle_quality_all(f_array_t p1, f_array_t p2, f_array_t p3) {
    auto pts1 = p1.unchecked<2>();
    auto pts2 = p2.unchecked<2>();
    auto pts3 = p3.unchecked<2>();

    ssize_t n = pts1.shape(0);
    f_array_t quality(n);
    auto q = quality.mutable_unchecked<1>();
    std::array<double, 9> vars;
    double vol, den;

    for (ssize_t i = 0; i < n; ++i) {
        vars[0] = pts2(i, 0) - pts1(i, 0);  // x2 - x1
        vars[1] = pts2(i, 1) - pts1(i, 1);  // y2 - y1
        vars[2] = pts2(i, 2) - pts1(i, 2);  // z2 - z1
        vars[3] = pts3(i, 0) - pts1(i, 0);  // x3 - x1
        vars[4] = pts3(i, 1) - pts1(i, 1);  // y3 - y1
        vars[5] = pts3(i, 2) - pts1(i, 2);  // z3 - z1
        vars[6] = pts3(i, 0) - pts2(i, 0);  // x3 - x2
        vars[7] = pts3(i, 1) - pts2(i, 1);  // y3 - y2
        vars[8] = pts3(i, 2) - pts2(i, 2);  // z3 - z2
        auto n = cross(vars[0], vars[1], vars[2], vars[3], vars[4], vars[5]);
        vol = 0.5 * norm(n[0], n[1], n[2]);
        den = norm_sq(vars[0], vars[1], vars[2]) +
              norm_sq(vars[3], vars[4], vars[5]) +
              norm_sq(vars[6], vars[7], vars[8]);
        q(i) = 6.928203230275509 * vol / den;
    }
    return quality;
}

std::size_t pair_hash::operator()(const pair_t& pair) const noexcept {
    return pair.first <= pair.second
               ? pair.second * pair.second + pair.first
               : pair.first * (pair.first + 1) + pair.second;
}

i_array_t _triangle_find_edges(i_array_t f2v) {
    auto f2v_ = f2v.unchecked<2>();
    std::unordered_set<pair_t, pair_hash> edge_set;
    for (int i = 0; i < f2v_.shape(0); ++i) {
        for (int j = 0; j < 3; ++j) {
            unsigned n1 = f2v_(i, idx1[j]);
            unsigned n2 = f2v_(i, idx2[j]);
            auto e_curr =
                n1 < n2 ? std::make_pair(n1, n2) : std::make_pair(n2, n1);
            edge_set.insert(e_curr);
        }
    }

    i_array_t edges({static_cast<py::ssize_t>(edge_set.size()),
                     static_cast<py::ssize_t>(2)});
    auto edges_ = edges.mutable_unchecked<2>();
    ssize_t i = 0;
    for (auto edge : edge_set) {
        edges_(i, 0) = edge.first;
        edges_(i, 1) = edge.second;
        i++;
    }
    return edges;
}

_TriangleConnectivity::_TriangleConnectivity(py::array_t<int> f2v) {
    auto f2v_ = f2v.mutable_unchecked<2>();
    std::unordered_map<pair_t, pair_t, pair_hash> edge_map;
    for (int i = 0; i < f2v_.shape(0); ++i) {
        for (int j = 0; j < 3; ++j) {
            unsigned n1 = f2v_(i, idx1[j]);
            unsigned n2 = f2v_(i, idx2[j]);
            auto e_curr =
                n1 < n2 ? std::make_pair(n1, n2) : std::make_pair(n2, n1);
            auto it = edge_map.find(e_curr);

            if (it == edge_map.end()) {
                edge_map[e_curr] = std::make_pair(i, j);
            } else {
                auto pair1 = std::make_pair(i, j);
                auto pair2 = it->second;
                connectivity_[pair1] = pair2;
                connectivity_[pair2] = pair1;
            }
        }
    }
}

/* Edge flip
An edge flip is a local operation between two adjacent triangles that
attempts to improve the quality of the mesh. The operation is demonstrated
as follows
       ___________                 ____________
      /     ____//   edge flip    /\__        /
     / ____/    /    =========>  /     \__   /
    /_/________/                /__________\/
or in indices
f2v = [0,  1,  2]    =========>    [0,  1,  3]
      [0,  2,  3]                  [1,  2,  3]
*/
void _TriangleConnectivity::_update_connectivity(py::array_t<double> pos,
                                                 py::array_t<int> f2v) {
    auto f2v_ = f2v.mutable_unchecked<2>();
    for (int f1 = 0; f1 < f2v_.shape(0); ++f1) {
        for (int e1 = 0; e1 < 3; ++e1) {
            auto match = connectivity_.find(std::make_pair(f1, e1));
            if (match == connectivity_.end()) continue;  // no matched edge
            int f2 = match->second.first;
            int e2 = match->second.second;

            auto x1 = py::cast<f_array_t>(  // pos[f2v[f1, 0], :]
                pos[py::make_tuple(f2v_(f1, 0), py::ellipsis())]);
            auto x2 = py::cast<f_array_t>(  // pos[f2v[f1, 1], :]
                pos[py::make_tuple(f2v_(f1, 1), py::ellipsis())]);
            auto x3 = py::cast<f_array_t>(  // pos[f2v[f1, 2], :]
                pos[py::make_tuple(f2v_(f1, 2), py::ellipsis())]);
            auto y1 = py::cast<f_array_t>(  // pos[f2v[f2, 0], :]
                pos[py::make_tuple(f2v_(f2, 0), py::ellipsis())]);
            auto y2 = py::cast<f_array_t>(  // pos[f2v[f2, 1], :]
                pos[py::make_tuple(f2v_(f2, 1), py::ellipsis())]);
            auto y3 = py::cast<f_array_t>(  // pos[f2v[f2, 2], :]
                pos[py::make_tuple(f2v_(f2, 2), py::ellipsis())]);

            double q1 = _triangle_quality(x1, x2, x3);
            double q2 = _triangle_quality(y1, y2, y3);
            double prev_min_q = std::min(q1, q2);

            if (prev_min_q < 0.9) {
                // Two temporary triangles to test the edge flip
                std::array<int, 3> tri1{f2v_(f1, 0), f2v_(f1, 1), f2v_(f1, 2)};
                std::array<int, 3> tri2{f2v_(f2, 0), f2v_(f2, 1), f2v_(f2, 2)};

                // Swap edges
                tri1[idx2[e1]] = tri2[e2];
                tri2[idx2[e2]] = tri1[e1];

                auto u1 = py::cast<f_array_t>(
                    pos[py::make_tuple(tri1[0], py::ellipsis())]);
                auto u2 = py::cast<f_array_t>(
                    pos[py::make_tuple(tri1[1], py::ellipsis())]);
                auto u3 = py::cast<f_array_t>(
                    pos[py::make_tuple(tri1[2], py::ellipsis())]);
                auto v1 = py::cast<f_array_t>(
                    pos[py::make_tuple(tri2[0], py::ellipsis())]);
                auto v2 = py::cast<f_array_t>(
                    pos[py::make_tuple(tri2[1], py::ellipsis())]);
                auto v3 = py::cast<f_array_t>(
                    pos[py::make_tuple(tri2[2], py::ellipsis())]);

                q1 = _triangle_quality(u1, u2, u3);
                q2 = _triangle_quality(v1, v2, v3);
                double curr_min_q = std::min(q1, q2);

                if (curr_min_q > prev_min_q + 0.025) {
                    f_array_t n1 = _triangle_normal(u1, u2, u3);
                    f_array_t n2 = _triangle_normal(v1, v2, v3);
                    f_array_t n3 = _triangle_normal(x1, x2, x3);
                    f_array_t n4 = _triangle_normal(y1, y2, y3);
                    auto n1_ = n1.unchecked<1>();
                    auto n2_ = n2.unchecked<1>();
                    auto n3_ = n3.unchecked<1>();
                    auto n4_ = n4.unchecked<1>();
                    bool flip = (dot(n1_(0), n1_(1), n1_(2), n2_(0), n2_(1),
                                     n2_(2)) > 0) &&
                                (dot(n3_(0), n3_(1), n3_(2), n4_(0), n4_(1),
                                     n4_(2)) > 0);

                    if (flip) {
                        // Insert new triangles
                        f2v_(f1, 0) = tri1[0];
                        f2v_(f1, 1) = tri1[1];
                        f2v_(f1, 2) = tri1[2];
                        f2v_(f2, 0) = tri2[0];
                        f2v_(f2, 1) = tri2[1];
                        f2v_(f2, 2) = tri2[2];

                        auto pair1 = std::make_pair(f1, idx1[e1]);
                        auto pair2 = std::make_pair(f2, idx1[e2]);
                        auto pair3 = std::make_pair(f1, e1);
                        auto pair4 = std::make_pair(f2, e2);

                        // Share connectivity info of the exchanged edge
                        auto it1 = connectivity_.find(pair2);
                        if (it1 != connectivity_.end()) {
                            connectivity_[pair3] = it1->second;
                            connectivity_[it1->second] = pair3;

                        } else {
                            connectivity_.erase(pair3);
                        }

                        auto it2 = connectivity_.find(pair1);
                        if (it2 != connectivity_.end()) {
                            connectivity_[pair4] = it2->second;
                            connectivity_[it2->second] = pair4;
                        } else {
                            connectivity_.erase(pair4);
                        }

                        // Add the flipped edge
                        connectivity_[pair1] = pair2;
                        connectivity_[pair2] = pair1;

                    }  // if flip
                }  // if curr_min_q > prev_min_q + 0.025
            }  // if prev_min_q < 0.9
        }  // for e1
    }  // for f1
}  // _update_connectivity

PYBIND11_MODULE(_triangle_utils, m) {
    m.def("_triangle_area", &_triangle_area);
    m.def("_triangle_area_all", &_triangle_area_all);
    m.def("_triangle_normal", &_triangle_normal);
    m.def("_triangle_normal_all", &_triangle_normal_all);
    m.def("_triangle_quality", &_triangle_quality);
    m.def("_triangle_quality_all", &_triangle_quality_all);
    m.def("_triangle_find_edges", &_triangle_find_edges);
    py::class_<_TriangleConnectivity>(m, "_TriangleConnectivity")
        .def(py::init<f_array_t>())
        .def("_update_connectivity",
             &_TriangleConnectivity::_update_connectivity);
}