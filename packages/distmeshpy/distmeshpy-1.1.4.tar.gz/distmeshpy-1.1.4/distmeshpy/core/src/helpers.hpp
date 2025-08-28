#ifndef HELPERS_HPP
#define HELPERS_HPP

/* Helper math functions */
template <typename T>
inline T dot(T const &u1, T const &u2, T const &u3, T const &v1, T const &v2,
             T const &v3) {
    return u1 * v1 + u2 * v2 + u3 * v3;
}

template <typename T>
inline std::array<T, 3> cross(T const &u1, T const &u2, T const &u3,
                              T const &v1, T const &v2, T const &v3) {
    return {u2 * v3 - u3 * v2, u3 * v1 - u1 * v3, u1 * v2 - u2 * v1};
}

template <typename T>
inline T norm_sq(T const &v1, T const &v2, T const &v3) {
    return dot(v1, v2, v3, v1, v2, v3);
}

template <typename T>
inline T norm(T const &v1, T const &v2, T const &v3) {
    return std::sqrt(norm_sq(v1, v2, v3));
}

#endif  // !HELPERS_HPP