#ifndef TRIDRAW_H
#define TRIDRAW_H

#include <stdint.h>

void tris_raster(
    int rows_fb, int cols_fb, double frame_buffer[rows_fb][cols_fb][3],
    int n_tris, const int32_t triangles [n_tris][2][3], const double tricolors[n_tris][3]
);

#endif