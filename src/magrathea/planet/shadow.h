#ifndef shadow_h
#define shadow_h

void cast_shadow(
     double* shade,
     const double *r_view_b, // treat as double[3]
     const double *r_light_b,
     const double rr_light,
     const double *r_caster_b,
     const double rr_caster,
     int verbose
);

#endif