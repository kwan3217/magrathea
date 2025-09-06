#include "tridraw.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static inline int inside_triangle(const int pts[2][3], int Px, int Py) {
    int cross0 = (pts[0][1] - pts[0][0]) * (Py - pts[1][0]) - (pts[1][1] - pts[1][0]) * (Px - pts[0][0]);
    int cross1 = (pts[0][2] - pts[0][1]) * (Py - pts[1][1]) - (pts[1][2] - pts[1][1]) * (Px - pts[0][1]);
    int cross2 = (pts[0][0] - pts[0][2]) * (Py - pts[1][2]) - (pts[1][0] - pts[1][2]) * (Px - pts[0][2]);
    return (cross0 >= 0 && cross1 >= 0 && cross2 >= 0);
}

static inline void triangle(int rows_fb, int cols_fb, double frame_buffer[rows_fb][cols_fb][3], const int pts[2][3], const double color[3]) {
    int bboxmin_x = cols_fb - 1, bboxmin_y = rows_fb - 1;
    int bboxmax_x = 0, bboxmax_y = 0;
    int clamp_x = cols_fb - 1, clamp_y = rows_fb - 1;
    for (int i = 0; i < 3; i++) {
        bboxmin_x = (0 > pts[0][i]) ? 0 : (bboxmin_x < pts[0][i] ? bboxmin_x : pts[0][i]);
        bboxmin_y = (0 > pts[1][i]) ? 0 : (bboxmin_y < pts[1][i] ? bboxmin_y : pts[1][i]);
        bboxmax_x = (clamp_x < pts[0][i]) ? clamp_x : (bboxmax_x > pts[0][i] ? bboxmax_x : pts[0][i]);
        bboxmax_y = (clamp_y < pts[1][i]) ? clamp_y : (bboxmax_y > pts[1][i] ? bboxmax_y : pts[1][i]);
    }
    for (int Px = bboxmin_x; Px <= bboxmax_x; Px++) {
        for (int Py = bboxmin_y; Py <= bboxmax_y; Py++) {
            if (!inside_triangle(pts, Px, Py)) continue;
            for (int i_rgb = 0; i_rgb < 3; i_rgb++) {
                frame_buffer[Py][Px][i_rgb] = color[i_rgb];
            }
        }
    }
}

void tris_draw(
    int rows_fb, int cols_fb, double frame_buffer[rows_fb][cols_fb][3],
    int n_tris, const int32_t triangles[n_tris][2][3], const double tricolors[3][n_tris]
) {
    for(int i_tri=0;i_tri<n_tris;i_tri++) triangle(rows_fb,cols_fb,frame_buffer,triangles[i_tri],tricolors[i_tri]);
}