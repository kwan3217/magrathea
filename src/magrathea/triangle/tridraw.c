#include "tridraw.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static inline int edge_function(int va[2], int vb[2], int x, int y) {
  return (x - va[0]) * (vb[1] - va[1]) - (y - va[1]) * (vb[0] - va[0]);
}

static inline int min3(int triangle[3]) {
  int min_val = triangle[0];
  for(int i=1;i<3;i++) if (triangle[i] < min_val) min_val = triangle[i];
  return min_val;
}

static inline int max3(int triangle[3]) {
  int max_val = triangle[0];
  for(int i=1;i<3;i++) if (triangle[i] > max_val) max_val = triangle[i];
  return max_val;
}

static inline void tri_raster(int H, int W, double frame_buffer[H][W][3],
                              const int32_t triangle[2][3], const double tricolor[3]) {
  // Compute bounding box
  int x_min = min3(triangle[0]);
  int x_max = max3(triangle[0]);
  int y_min = min3(triangle[1]);
  int y_max = max3(triangle[1]);

  // Clamp to frame buffer bounds
  x_min = 0>x_min?0:x_min;
  x_max = W-1<x_max?W-1:x_max;
  y_min = 0>y_min?0:y_min;
  y_max = H-1<y_max?H-1:y_max;

  // Skip if bounding box is empty
  if (x_max < x_min || y_max < y_min) return;

  // Create 2D grid of pixel centers
  for(int i_y=y_min;i_y<=y_max;i_y++) {
    for(int i_x=x_min;i_x<=x_max;i_x++) {

      // Compute edge functions over grid
      int in_edge0 = edge_function((int[2]){triangle[0][1],triangle[1][1]},(int[2]){triangle[0][2],triangle[1][2]}, i_x, i_y);  // V1 -> V2
      int in_edge1 = edge_function((int[2]){triangle[0][2],triangle[1][2]},(int[2]){triangle[0][0],triangle[1][0]}, i_x, i_y);  // V2 -> V0
      int in_edge2 = edge_function((int[2]){triangle[0][0],triangle[1][0]},(int[2]){triangle[0][1],triangle[1][1]}, i_x, i_y);  // V0 -> V1

      // Pixels inside triangle (all edge functions >= 0)
      int in_triangle = (in_edge0 >= 0) && (in_edge1 >= 0) && (in_edge2 >= 0);

      // Assign color to frame buffer
      if(in_triangle) {
        for(int i_rgb=0;i_rgb<3;i_rgb++) frame_buffer[i_y][i_x][i_rgb] = tricolor[i_rgb];
      }
    }
  }
}

void tris_raster(int rows_fb, int cols_fb, double frame_buffer[rows_fb][cols_fb][3],
               int n_tris, const int32_t triangles[n_tris][2][3], const double tricolors[n_tris][3]) {
  for(int i_tri=0;i_tri<n_tris;i_tri++) {
    tri_raster(rows_fb,cols_fb,frame_buffer,triangles[i_tri],tricolors[i_tri]);
  }
}
