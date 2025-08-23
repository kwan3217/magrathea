#include "shadow.h"
#include <math.h>
#include <stdio.h>

static inline double clip(double n, double a, double b) {
    if(n<a) return a;
    if(n>b) return b;
    return n;
}

static inline double vlength(double a[3]) {
    return sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]);
}

static inline double vdot(double a[3], double b[3]) {
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
}

static inline double vangle(double a[3], double b[3]) {
    return acos(clip(vdot(a,b)/(vlength(a)*vlength(b)),-1.0,1.0));
}

//#define PrintVector(x) if(verbose) printf(#x ": <%f,%f,%f>\n",x[0],x[1],x[2])
//#define PrintNumber(x) if(verbose) printf(#x ": %f\n",x)

void cast_shadow(double *shade,
                 const double r_view_b[3], // treat as double[3]
                 const double r_light_b[3], const double rr_light,
                 const double r_caster_b[3], const double rr_caster,
                 int verbose) {
  /*
  Cast a shadow on a set of points
  :param shade: M,N array of shade values, originally all 1.0. This code can
  scale down any value in this array to indicate shade. 1=100% lighting, 0=0%
  lighting. May be NaN if r_view_b is NaN at this pixel. :param r_view_b: M,3,N
  array of points that may be shaded. Any point *may* be [[NaN],[NaN],[NaN]] and
  this must be handled. :param r_light_b: 3,1 column vector position of Sun
  :param rr_light: radius of sun
  :param rs_caster_b: 3,1 column vector position of shadow caster
  :param rr_caster: radius of caster
  All distance units, for vector components and sphere radii, must be
  consistent. Spice will naturally be in km.
  */
  // Early exit for NaN
  if (isnan(r_view_b[0])) {
    *shade = NAN;
    return;
  }
  // Vector from view to caster and to light
  double dr_light[3];
  for (int i = 0; i < 3; i++)
    dr_light[i] = r_light_b[i] - r_view_b[i];
  double dr_caster[3];
  for (int i = 0; i < 3; i++)
    dr_caster[i] = r_caster_b[i] - r_view_b[i];
  // angle between caster and light
  double alpha_sep = vangle(dr_light, dr_caster);
  // Distance to light and caster
  double d_light = vlength(dr_light);
  double d_caster = vlength(dr_caster);
  // half angle of light and caster
  double theta_light  = acos(sqrt(1 - (rr_light  * rr_light ) / (d_light  * d_light )));
  double theta_caster = acos(sqrt(1 - (rr_caster * rr_caster) / (d_caster * d_caster)));
  // Points with any shadow at all, total annular or partial
  int occlusion_mask = (alpha_sep < theta_light + theta_caster);
  // Points totally eclipsed -- caster is larger than light source
  int total_mask = occlusion_mask & (theta_caster >= theta_light) &
                   (alpha_sep <= theta_caster - theta_light);
  if (total_mask) {
    *shade = 0.0; // full shadow
    return;
  }
  // Points annularly eclipsed -- caster is smaller and completely inside light
  // source
  int annular_mask = occlusion_mask & (theta_caster < theta_light) &
                     (alpha_sep <= theta_light - theta_caster);
  if (annular_mask) {
    *shade *= 1.0 - (theta_caster * theta_caster / (theta_light * theta_light));
  }
  // Complicated case -- points partially eclipsed.
  int partial_mask = occlusion_mask & ~total_mask & ~annular_mask;

  // Precompute terms for A (vectorized over partial pixels)
  if (partial_mask) {
    double d = alpha_sep;     // separation
    double r1 = theta_light;  // light half-angle
    double r2 = theta_caster; // caster half-angle

    // Clamp for arccos stability
    double arg1 = clip((d * d + r1 * r1 - r2 * r2) / (2 * d * r1), -1.0, 1.0);
    double arg2 = clip((d * d + r2 * r2 - r1 * r1) / (2 * d * r2), -1.0, 1.0);

    double term1 = r1 * r1 * acos(arg1);
    double term2 = r2 * r2 * acos(arg2);
    double term3 = 0.5 * sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) *
                              (d + r1 + r2));
    double A = term1 + term2 - term3;

    // Obscured fraction f = A / (pi * theta_light^2)
    double f_partial = A / (M_PI * r1 * r1);

    // Update lighting
    *shade *= 1.0 - f_partial;
  }
}

//#undef PrintVector
