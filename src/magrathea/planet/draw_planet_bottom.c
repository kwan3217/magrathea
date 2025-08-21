#include "draw_planet_bottom.h"
#include <math.h>
#include <stdio.h>

static inline double linterp(double x0, double y0, double x1, double y1, double x) {
  double t=(x-x0)/(x1-x0);
  return (1-t)*y0+t*y1;
}

static inline double vdot(double a[3], double b[3]) {
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
}

static inline void GEOD(double r, double z, double a, double b, double *fi/*, double *h*/) {
  // Blind idiot translation of Borkowski fortran geodetic conversion
  /* Program to transform Cartesian to geodetic coordinates
      Input:   r, z = equatorial and polar components
               a, b = equatorial and polar radii
      Output: fi, h = geodetic coords (latitude [rad], height [same units as r,z,a,b]) */
  b = copysign(b, z);
  double E = ((z + b) * b / a - a) / r;
  double F = ((z - b) * b / a + a) / r;
  double P = (E * F + 1.) * 4. / 3.;
  double Q = (E * E - F * F) * 2.;
  double D = P * P * P + Q * Q;
  double v;
  if (D >= 0.0) {
    double s = sqrt(D) + Q;
    s = cbrt(s);
    v = P / s - s;
    v = -(Q + Q + v * v * v) / (3 * P);
  } else {
    v = 2. * sqrt(-P) * cos(acos(Q / P / sqrt(-P)) / 3.);
  }
  double G = .5 * (E + sqrt(E * E + v));
  double t = sqrt(G * G + (F - v * G) / (G + G - E)) - G;
  *fi = atan((1. - t * t) * a / (2 * b * t));
  /* Our use case is always on the ellipsoid surface so we don't care about h */
  //*h = (r - a * t) * cos(*fi) + (z - b) * sin(*fi);
}

static inline void xyz2ll_deg(double xyz[3], double re, double rp, double* lat_deg, double* lon_deg) {
  // wrapper for GEOD to match interface for lat,lon,_=xyz2lla(centric=False,deg=True,xyz=r_surf_b,re=n[0],rp=n[2],east=True)
  *lon_deg=atan2(xyz[1],xyz[0])*180/M_PI;
  GEOD(sqrt(xyz[0]*xyz[0]+xyz[1]*xyz[1]),xyz[2],re,rp,lat_deg);
  *lat_deg*=180/M_PI;
}

static inline double wrap_angle(double angle) {
    double wrapped = fmod(angle, 360.0);
    return wrapped < 0.0 ? wrapped + 360.0 : wrapped;
}

int draw_planet_bottom(
    double *frame_buffer_data, int rows_fb, int cols_fb,
    const double *texture_map_data, int rows_tm, int cols_tm,
    double extra_rot,
    const double right_b[3],
    const double down_b[3],
    const double direction_b[3],
    const double r_viewpoint_b[3],
    const double n[3],
    const double n2[3],
    const double r_light_b[3]
) {
    double R0n[3];
    for(int i=0;i<3;i++) R0n[i]=r_viewpoint_b[i]/n[i];
    for (int i_row = 0; i_row < rows_fb; i_row++) {
        double y_n=linterp(0,-0.5,rows_fb,0.5,i_row);
        for (int i_col = 0; i_col < cols_fb; i_col++) {
            /* From here down, all calculations are done in the ellipsoid body frame */

            /** Use the camera vectors to generate rays for all pixels. The r0 is the viewpoint in the body frame,
                and v is calculated as a linear combination of down_b, right_b, and direction_b using normalized
                image coordinates ranging from -0.5 on top and left to +0.5 on bottom and right. */
            double x_n=linterp(0,-0.5,cols_fb,0.5,i_col);
            double v_b[3];
            for(int i=0;i<3;i++) v_b[i]=down_b[i]*y_n+right_b[i]*x_n+direction_b[i];

            /*(* Solve the ray-ellipsoid intersection for all rays */
            double Vn[3];
            for(int i=0;i<3;i++) Vn[i]=v_b[i]/n[i];
            double A=vdot(Vn,Vn);
            double B=2*vdot(R0n,Vn);
            double C=vdot(R0n,R0n)-1;
            double D=B*B-4*A*C;
            if(D<0) continue;
            double tp=(-B+sqrt(D))/(2*A);
            double tm=(-B-sqrt(D))/(2*A);
            if(tp<0 && tm<0) continue;
            double t;
            if(tp>0 && tp<tm) {
                t=tp;
            } else {
                t=tm;
            }

            /** Calculate the normal vector at all intersections */
            double r_surf_b[3];
            for(int i=0;i<3;i++) r_surf_b[i]=r_viewpoint_b[i]+v_b[i]*t;

            /* The ellipsoid is a level surface of the function F(x,y,z)=(x/r_e)**2+(y/r_e)**2+(z/r_p)**2, and we want the
               normal for this surface at F=1. The gradient of F is normal to all its level surfaces, so we want the gradient
               at this point. The gradient is [[dF/dx],[dF/dy],[dF/dz]] so we have N=[[2x/r_e**2],[2y/r_e**2],[2z/r_p**2]]=2*R./[[r_e**2],[r_e**2],[r_p**2]]
               We only care about the direction, so normalize the normal vector. */
            double N[3];
            for(int i=0;i<3;i++) N[i]=2*r_surf_b[i]/n2[i];
            double Nlen=sqrt(vdot(N,N));
            double Nhat[3];
            for(int i=0;i<3;i++) Nhat[i]=N[i]/Nlen;
            /** Calculate the brightness model at all intersections. Eventually this will include shadow casters. */
            double L[3];
            for(int i=0;i<3;i++) L[i]=r_light_b[i]-r_surf_b[i];
            double Llen=sqrt(vdot(L,L));
            double Lhat[3];
            for(int i=0;i<3;i++) Lhat[i]=L[i]/Llen; //Direction from point on surface to light source
            double dot= vdot(Lhat,Nhat);
            double lambert=0.9*(dot>0?dot:0);
            double ambient=0.1;
            double bright=lambert+ambient;
            /** Calculate latitude and longitude at all intersections */
            double lat,lon; // both in degrees
            //lat,lon,_=xyz2lla(centric=False,deg=True,xyz=r_surf_b,re=n[0],rp=n[2],east=True)
            xyz2ll_deg(r_surf_b,n[0],n[2],&lat,&lon);
            /** Interpolate the texture map using latitude and longitude */
            //rows_tm=texture_map.shape[0] # number of columns
            //cols_tm=texture_map.shape[1] # number of rows
            int x_tex=(int)(linterp(0.0,0.0,360.0,cols_tm-1,wrap_angle(lon+extra_rot)));  //RIP Ariane 5 Flight 1
            int y_tex=(int)(linterp(90.0,0.0,-90.0,rows_tm-1,lat));
            /** Scale the texture color by the brightness. This is the color for each pixel that has an intersection
              * For pixels with intersections, overwrite the frame buffer color with the calculated color. Pixels with
                no intersections have already taken an early exit */
            int fb_idx = (i_row * cols_fb + i_col) * 3;  // RGB pixel index
            int tm_idx = (y_tex * cols_tm + x_tex) * 3;
            for(int i=0;i<3;i++) frame_buffer_data[fb_idx+i]=texture_map_data[tm_idx+i]*bright;
        }
    }
    return 0; // Success
}