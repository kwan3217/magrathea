# cython: language_level=3


cimport numpy as np
import numpy as np
from libc.stdint cimport int32_t

cdef extern from "tridraw.h":
    void tris_raster(
        int rows_fb, int cols_fb, double *frame_buffer_data,
        int n_tris, const int32_t *triangles, const double* tricolors
    )

def tris_raster_c(
    np.ndarray[np.float64_t, ndim=3] frame_buffer not None,
    np.ndarray[np.int32_t, ndim=3] triangles not None,
    np.ndarray[np.float64_t, ndim=2] tricolors not None,
):
    # Validate shapes
    if frame_buffer.shape[2] != 3:
        raise ValueError(f"Frame buffer must be (H,W,3)")
    if triangles.shape[1]!=2 or triangles.shape[2]!=3:
        raise ValueError(f"Triangles must be (N,2,3)")
    if tricolors.shape[1]!=3:
        raise ValueError(f"Tricolors must be (N,3)")
    if triangles.shape[0]!=tricolors.shape[0]:
        raise ValueError(f"Triangles and tricolors must have same N")

    # Extract dimensions
    cdef int rows_fb = frame_buffer.shape[0]
    cdef int cols_fb = frame_buffer.shape[1]
    cdef int n_tris=triangles.shape[0]

    # Call C function
    tris_raster(
        rows_fb, cols_fb, <double*> frame_buffer.data,
        n_tris, <int32_t*> triangles.data, <double *> tricolors.data
    )

