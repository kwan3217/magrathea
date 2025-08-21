# cython: language_level=3

cimport numpy as np
import numpy as np
from libc.stdint cimport uint8_t

cdef extern from "draw_planet_bottom.h":
    int draw_planet_bottom(
        uint8_t *frame_buffer_data, int rows_fb, int cols_fb,
        const uint8_t *texture_map_data, int rows_tm, int cols_tm,
        double extra_rot,
        const double right_b[3],
        const double down_b[3],
        const double direction_b[3],
        const double r_viewpoint_b[3],
        const double n[3],
        const double n2[3],
        const double r_light_b[3]
    )

def py_draw_planet_bottom(
    np.ndarray[np.float64_t, ndim=3] frame_buffer not None,
    np.ndarray[np.float64_t, ndim=3] texture_map not None,
    double extra_rot,
    np.ndarray[np.float64_t, ndim=2] right_b not None,
    np.ndarray[np.float64_t, ndim=2] down_b not None,
    np.ndarray[np.float64_t, ndim=2] direction_b not None,
    np.ndarray[np.float64_t, ndim=2] r_viewpoint_b not None,
    np.ndarray[np.float64_t, ndim=2] n not None,
    np.ndarray[np.float64_t, ndim=2] n2 not None,
    np.ndarray[np.float64_t, ndim=2] r_light_b not None
):
    # Validate shapes
    #if (right_b.shape != (3,1) or down_b.shape != (3,1) or direction_b.shape != (3,1) or
    #    r_viewpoint_b.shape != (3,1) or n.shape != (3,1) or n2.shape != (3,1) or
    #    r_light_b.shape != (3,1)):
    #    raise ValueError("Vectors must be shape (3,1)")
    #if frame_buffer.shape[2] != 3 or texture_map.shape[2] != 3:
    #    raise ValueError("Frame buffer and texture map must be RGB (dim 3)")

    # Extract dimensions
    cdef int rows_fb = frame_buffer.shape[0]
    cdef int cols_fb = frame_buffer.shape[1]
    cdef int rows_tm = texture_map.shape[0]
    cdef int cols_tm = texture_map.shape[1]

    # Flatten 2D (3,1) arrays to 1D for C
    cdef double[3] right_b_flat
    cdef double[3] down_b_flat
    cdef double[3] direction_b_flat
    cdef double[3] r_viewpoint_b_flat
    cdef double[3] n_flat
    cdef double[3] n2_flat
    cdef double[3] r_light_b_flat
    for i in range(3):
        right_b_flat[i] = right_b[i,0]
        down_b_flat[i] = down_b[i,0]
        direction_b_flat[i] = direction_b[i,0]
        r_viewpoint_b_flat[i] = r_viewpoint_b[i,0]
        n_flat[i] = n[i,0]
        n2_flat[i] = n2[i,0]
        r_light_b_flat[i] = r_light_b[i,0]

    # Call C function
    cdef int result = draw_planet_bottom(
        <uint8_t*> frame_buffer.data, rows_fb, cols_fb,
        <uint8_t*> texture_map.data, rows_tm, cols_tm,
        extra_rot,
        right_b_flat,
        down_b_flat,
        direction_b_flat,
        r_viewpoint_b_flat,
        n_flat,
        n2_flat,
        r_light_b_flat
    )

    if result != 0:
        raise RuntimeError(f"C function failed with code {result}")