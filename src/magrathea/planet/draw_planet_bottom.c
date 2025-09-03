#include "draw_planet_bottom.h"
#include "shadow.h"
#include <math.h>
#include <stdio.h>

static inline double linterp(double x0, double y0, double x1, double y1, double x) {
  double t=(x-x0)/(x1-x0);
  return (1-t)*y0+t*y1;
}

static inline double vdot(double a[3], double b[3]) {
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
}

// Simplified GEOD which takes advantage of the point in question being on the surface
static inline double GEOD(double r, double z, double a, double b) {
  double tan_phi = (a * a / (b * b)) * (z / r);
  double phi = atan(tan_phi);
  return phi;
}

static inline void xyz2ll_deg(double xyz[3], double re, double rp, double* lat_deg, double* lon_deg) {
  // wrapper for GEOD to match interface for lat,lon,_=xyz2lla(centric=False,deg=True,xyz=r_surf_b,re=n[0],rp=n[2],east=True)
  *lon_deg=atan2(xyz[1],xyz[0])*180/M_PI;
  double lat_rad=GEOD(sqrt(xyz[0]*xyz[0]+xyz[1]*xyz[1]),xyz[2],re,rp);
  *lat_deg=lat_rad*180/M_PI;
}

static inline double wrap_angle(double angle) {
    double wrapped = fmod(angle, 360.0);
    return wrapped < 0.0 ? wrapped + 360.0 : wrapped;
}

int draw_planet_bottom(
    int rows_fb, int cols_fb, double frame_buffer_data[rows_fb][cols_fb][3],
    int rows_tm, int cols_tm, const double texture_map_data[rows_tm][cols_tm][3],
    double extra_rot,
    const double right_b[3],
    const double down_b[3],
    const double direction_b[3],
    const double r_viewpoint_b[3],
    const double n[3],
    const double n2[3],
    const double r_light_b[3],
    const double rr_light,
    const double *rs_caster_b, const double *rrs_caster, int n_casters
) {
    double R0n[3];
    for(int i_comp=0;i_comp<3;i_comp++) R0n[i_comp]=r_viewpoint_b[i_comp]/n[i_comp];
    for (int y_fb = 0; y_fb < rows_fb; y_fb++) {
        double y_n=linterp(0,-0.5,rows_fb,0.5,y_fb);
        for (int x_fb = 0; x_fb < cols_fb; x_fb++) {
            /* From here down, all calculations are done in the ellipsoid body frame */

            /** Use the camera vectors to generate rays for all pixels. The r0 is the viewpoint in the body frame,
                and v is calculated as a linear combination of down_b, right_b, and direction_b using normalized
                image coordinates ranging from -0.5 on top and left to +0.5 on bottom and right. */
            double x_n=linterp(0,-0.5,cols_fb,0.5,x_fb);
            double v_b[3];
            for(int i_comp=0;i_comp<3;i_comp++) v_b[i_comp]=down_b[i_comp]*y_n+right_b[i_comp]*x_n+direction_b[i_comp];

            /*(* Solve the ray-ellipsoid intersection for all rays */
            double Vn[3];
            for(int i_comp=0;i_comp<3;i_comp++) Vn[i_comp]=v_b[i_comp]/n[i_comp];
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
            for(int i_comp=0;i_comp<3;i_comp++) r_surf_b[i_comp]=r_viewpoint_b[i_comp]+v_b[i_comp]*t;

            /* The ellipsoid is a level surface of the function F(x,y,z)=(x/r_e)**2+(y/r_e)**2+(z/r_p)**2, and we want the
               normal for this surface at F=1. The gradient of F is normal to all its level surfaces, so we want the gradient
               at this point. The gradient is [[dF/dx],[dF/dy],[dF/dz]] so we have N=[[2x/r_e**2],[2y/r_e**2],[2z/r_p**2]]=2*R./[[r_e**2],[r_e**2],[r_p**2]]
               We only care about the direction, so normalize the normal vector. */
            double N[3];
            for(int i_comp=0;i_comp<3;i_comp++) N[i_comp]=2*r_surf_b[i_comp]/n2[i_comp];
            double Nlen=sqrt(vdot(N,N));
            double Nhat[3];
            for(int i_comp=0;i_comp<3;i_comp++) Nhat[i_comp]=N[i_comp]/Nlen;
            /** Calculate the brightness model at all intersections */
            double L[3];
            for(int i_comp=0;i_comp<3;i_comp++) L[i_comp]=r_light_b[i_comp]-r_surf_b[i_comp];
            double Llen=sqrt(vdot(L,L));
            double Lhat[3];
            for(int i_comp=0;i_comp<3;i_comp++) Lhat[i_comp]=L[i_comp]/Llen; //Direction from point on surface to light source
            double dot= vdot(Lhat,Nhat);
            double lambert=(dot>0?dot:0);
            double shade=1.0;
            for(int i_caster=0;i_caster<n_casters;i_caster++) {
               double r_caster_b[3];for(int i_comp=0;i_comp<3;i_comp++) r_caster_b[i_comp]=rs_caster_b[i_comp*n_casters+i_caster];
               double rr_caster=rrs_caster[i_caster];
               cast_shadow(&shade,
                     r_surf_b,
                     r_light_b,
                     rr_light,
                     r_caster_b,
                     rr_caster,
                     (y_fb==214) && (x_fb==230));

            }
            double diffuse=0.9*lambert*shade;
            double ambient=0.1;
            double bright=diffuse+ambient;
            /** Calculate latitude and longitude at all intersections */
            double lat,lon; // both in degrees
            xyz2ll_deg(r_surf_b,n[0],n[2],&lat,&lon);
            /** Interpolate the texture map using latitude and longitude */
            int x_tex=(int)(linterp(0.0,0.0,360.0,cols_tm-1,wrap_angle(lon+extra_rot)));  //RIP Ariane 5 Flight 1
            int y_tex=(int)(linterp(90.0,0.0,-90.0,rows_tm-1,lat));
            /** Scale the texture color by the brightness. This is the color for each pixel that has an intersection
              * For pixels with intersections, overwrite the frame buffer color with the calculated color. Pixels with
                no intersections have already taken an early exit */
            for(int i_channel=0;i_channel<3;i_channel++) frame_buffer_data[y_fb][x_fb][i_channel]=texture_map_data[y_tex][x_tex][i_channel]*bright;
        }
    }
    return 0; // Success
}