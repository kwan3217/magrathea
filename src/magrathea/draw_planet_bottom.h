#ifndef DRAW_PLANET_BOTTOM_H
#define DRAW_PLANET_BOTTOM_H

#include <stdint.h>

int draw_planet_bottom(
    double *frame_buffer_data, int rows_fb, int cols_fb,
    const double *texture_map_data, int rows_tm, int cols_tm,
    double extra_rot,
    const double right_b[3],
    const double down_b[3],
    const double direction_b[3],
    const double r_viewpoint_b[3],
    const double n[3],    // Ellipsoid radii: [r_e, r_e, r_p]
    const double n2[3],   // Squared radii: [r_e^2, r_e^2, r_p^2]
    const double r_light_b[3]
);

#endif