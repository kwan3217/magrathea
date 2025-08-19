"""
Draw an ellipsoid into a frame buffer

Created: 8/18/25
"""
import numpy as np
from kwanmath.interp import linterp
from kwanmath.vector import vdot, vlength
from kwanmath.geodesy import xyz2lla
from spiceypy import spkezr, bodc2n, pxform, gdpool


def planet(*,
           frame_buffer:np.ndarray,
           down_u:np.ndarray,
           right_u:np.ndarray,
           direction_u:np.ndarray,
           ellipsoid_spice_id:int,
           view_spice_id:int,
           light_spice_id:int=10,
           et:float,
           shadow_casters_spice_ids:list[int]=None,
           universe_frame:str="J2000",
           texture_map:np.ndarray,
           r_viewpoint_b:np.ndarray=None,
           r_light_b:np.ndarray=None,
           M_bu:np.ndarray=None,
           extra_rot:float=0)->None:
    """
    Draw a texture-mapped ellipsoid into the frame buffer

    :param frame_buffer: frame buffer, an array of rgb pixels, appropriate for plotting onto a pyplot or saving
                         as a png (rows x cols x 3)
    :param down_u: down vector of camera in universe frame
    :param right_u: right vector of camera in universe frame
    :param direction_u: direction vector of camera in universe frame
    :param ellipsoid_spice_id: spice id of ellipsoid to be drawn, for instance 599 for Jupiter or 501 for Io
    :param view_spice_id: spice id for viewpoint, for instance -31 for Voyager
    :param light_spice_id: spice id of light source, 10=sun by default
    :param et: Spice ephemeris time of frame
    :param shadow_casters_spice_ids: list of spice ids of objects which might cast shadows on the
    :param universe_frame: frame of down, right, and direction vectors
    :param texture_map: texture map to use to draw planet
    :param r_viewpoint_b: If passed, use this as position of viewpoint in body frame instead of calculating it from spkezr
    :param M_bu: If passed, use this as transformation from universe to body instead of calculating it with pxform

    :return: None, but a side effect is that the ellipsoid in question is drawn on the frame buffer

    Algorithm:
    * Use spkezr to calculate the position of the ellipsoid relative to the viewpoint. Reverse this vector
      to get the position of the viewpoint relative to the ellipsoid. We do it this way because neither LT+S
      nor XLT+S is exactly what we want. We want the position of the spacecraft relative to the ellipsoid
      at the time that the photons from the ellipsoid arrive at the spacecraft at ET. So, we use LT+S to get
      the position of the ellipsoid relative to the viewer, then reverse the vector. We work in the body frame
      of the ellipsoid in any case.
    * Use pxform to get the rotation from universe to body frame at ET-LT, the orientation of the body at the time
      the light originates at the ellipsoid
    * Transform the camera vectors into the ellipsoid body frame
    From here down, all calculations are done in the ellipsoid body frame
    * Use the camera vectors to generate rays for all pixels. The r0 is the viewpoint in the body frame,
      and v is calculated as a linear combination of down_b, right_b, and direction_b using normalized
      image coordinates ranging from -0.5 on top and left to +0.5 on bottom and right.
    * Solve the ray-ellipsoid intersection for all rays
    * Calculate the normal vector at all intersections
    * Calculate the position of the light source at ET-LT using LT+S, with observer as ellipsoid center and target
      as light source.
    * Calculate the brightness model at all intersections. Eventually this will include shaders.
    * Calculate latitude and longitude at all intersections
    * Interpolate the texture map using latitude and longitude
    * Scale the texture color by the brightness. This is the color for each pixel that has an intersection
    * For pixels with intersections, overwrite the frame buffer color with the calculated color. Don't for
      pixels with no intersections.
    """
    # * Use spkezr to calculate the position of the ellipsoid relative to the viewpoint. Reverse this vector
    #   to get the position of the viewpoint relative to the ellipsoid. We do it this way because neither LT+S
    #   nor XLT+S is exactly what we want. We want the position of the spacecraft relative to the ellipsoid
    #   at the time that the photons from the ellipsoid arrive at the spacecraft at ET. So, we use LT+S to get
    #   the position of the ellipsoid relative to the viewer, then reverse the vector. We work in the body frame
    #   of the ellipsoid in any case.
    body_name=bodc2n(ellipsoid_spice_id)
    body_frame="IAU_"+body_name.upper()
    if r_viewpoint_b is None:
        x_ellipsoid_b,lt_ellipsoid=spkezr(str(ellipsoid_spice_id),et,body_frame,"LT+S",str(view_spice_id))
        x_viewpoint_b=-x_ellipsoid_b
        r_viewpoint_b=x_viewpoint_b[:3].reshape(-1,1) # form it into a column vector

    # * Use pxform to get the rotation from universe to body frame at ET-LT, the orientation of the body at the time
    #   the light originates at the ellipsoid
    if M_bu is None:
        et_ellipsoid=et-lt_ellipsoid
        M_bu=pxform(universe_frame,body_frame,et_ellipsoid)

    # * Transform the camera vectors into the ellipsoid body frame
    down_b=M_bu@down_u
    right_b=M_bu@right_u
    direction_b=M_bu@direction_u


    # From here down, all calculations are done in the ellipsoid body frame

    # * Use the camera vectors to generate rays for all pixels. The r0 is the viewpoint in the body frame,
    #   and v is calculated as a linear combination of down_b, right_b, and direction_b using normalized
    #   image coordinates ranging from -0.5 on top and left to +0.5 on bottom and right.
    rows_fb=frame_buffer.shape[0] # number of columns
    cols_fb=frame_buffer.shape[1] # number of rows
    # we want the camera vectors to be shape M,3,N. One plane of vectors 3,M represents one row
    # So we shape these so that they broadcast
    x_n=np.linspace(-0.5,0.5,cols_fb,endpoint=False).reshape( 1,1,-1)
    y_n=np.linspace(-0.5,0.5,rows_fb,endpoint=False).reshape(-1,1, 1)
    v_b=down_b*y_n+right_b*x_n+direction_b

    # * Solve the ray-ellipsoid intersection for all rays
    r_e,_,r_p=gdpool(f"BODY{ellipsoid_spice_id}_RADII",0,3)
    n=np.array([[r_e],[r_e],[r_p]])
    R0n=r_viewpoint_b/n
    Vn=v_b/n
    A=vdot(Vn,Vn)
    B=2*vdot(R0n,Vn)
    C=vdot(R0n,R0n)-1
    D=B**2-4*A*C
    with np.errstate(invalid='ignore'):
        # Points that are off-disk take the square root of a negative and return NaN. This is correct and expected.
        # Put this in an ignore to ignore this specific warning
        tp=(-B+np.sqrt(D))/(2*A)
        tm=(-B-np.sqrt(D))/(2*A)
    def choose_root(root1,root2):
        # Create a mask for positive roots
        pos1 = root1 > 0
        pos2 = root2 > 0

        # Initialize output with NaN
        result = np.full_like(root1, np.nan)

        # Case 1: Both roots positive, take the minimum
        both_positive = pos1 & pos2
        result[both_positive] = np.minimum(root1[both_positive], root2[both_positive])

        # Case 2: Only root1 is positive
        only_root1_positive = pos1 & ~pos2
        result[only_root1_positive] = root1[only_root1_positive]

        # Case 3: Only root2 is positive
        only_root2_positive = ~pos1 & pos2
        result[only_root2_positive] = root2[only_root2_positive]

        # Case 4: Both negative or both NaN -> result remains NaN
        return result
    t=choose_root(tp,tm)
    # * Calculate the normal vector at all intersections
    r_surf_b=r_viewpoint_b+v_b*t[:,None,:]
    # The ellipsoid is a level surface of the function F(x,y,z)=(x/r_e)**2+(y/r_e)**2+(z/r_p)**2, and we want the
    # normal for this surface at F=1. The gradient of F is normal to all its level surfaces, so we want the gradient
    # at this point. The gradient is [[dF/dx],[dF/dy],[dF/dz]] so we have N=[[2x/r_e**2],[2y/r_e**2],[2z/r_p**2]]=2*R./[[r_e**2],[r_e**2],[r_p**2]]
    # We only care about the direction, so normalize the normal vector.
    N=2*r_surf_b/np.array([[r_e**2],[r_e**2],[r_p**2]])
    Nlen=np.sqrt(vdot(N,N)[:,None,:])
    Nhat=N/Nlen
    # * Calculate the position of the light source at ET-LT using LT+S, with observer as ellipsoid center and target
    #   as light source.
    if r_light_b is None:
        x_light_b,_=spkezr(str(light_spice_id),et_ellipsoid,body_frame,"LT+S",str(ellipsoid_spice_id))
        r_light_b=x_light_b[:3].reshape(-1,1)
    # * Calculate the brightness model at all intersections. Eventually this will include shaders.
    L=r_light_b-r_surf_b
    Llen=np.sqrt(vdot(L,L)[:,None,:])
    Lhat=L/Llen #Direction from point on surface to light source
    lambert=0.9*np.maximum(0,vdot(Lhat,Nhat))
    ambient=0.1
    bright=lambert+ambient
    # * Calculate latitude and longitude at all intersections
    lat,lon,_=xyz2lla(centric=False,deg=True,xyz=r_surf_b,re=r_e,rp=r_p,east=True)
    # * Interpolate the texture map using latitude and longitude
    rows_tm=texture_map.shape[0] # number of columns
    cols_tm=texture_map.shape[1] # number of rows
    valid=np.isfinite(lat)
    with np.errstate(invalid='ignore'):
        # Points that are off-disk get NaN which don't map cleanly to int (and are coerced to 0 in this case).
        # Put this in an ignore to ignore this specific warning
        x_tex=linterp(0.0,0.0,360.0,cols_tm-1,(lon+extra_rot)%360.0).astype(np.uint16)  #RIP Ariane 5 Flight 1
        y_tex=linterp(90.0,0.0,-90.0,rows_tm-1,lat).astype(np.uint16)
    # * Scale the texture color by the brightness. This is the color for each pixel that has an intersection
    # * For pixels with intersections, overwrite the frame buffer color with the calculated color. Don't for
    #   pixels with no intersections.
    frame_buffer[:]=np.where(valid[...,None],texture_map[y_tex,x_tex,:]*bright[...,None],frame_buffer)


def planets(*,
            frame_buffer:np.ndarray,
            down_u:np.ndarray,
            right_u:np.ndarray,
            direction_u:np.ndarray,
            view_spice_id:int,
            light_spice_id:int=10,
            et:float,
            universe_frame:str="J2000",
            texture_maps:dict[int,np.ndarray],
            extra_rots:dict[int,float]=None):
    """
    Draw multiple ellipsoids
    :param frame_buffer: frame buffer, an array of rgb pixels, appropriate for plotting onto a pyplot or saving
                         as a png (rows x cols x 3)
    :param down_u: down vector of camera in universe frame
    :param right_u: right vector of camera in universe frame
    :param direction_u: direction vector of camera in universe frame
    :param view_spice_id: spice id for viewpoint, for instance -31 for Voyager
    :param light_spice_id: spice id of light source, 10=sun by default
    :param et: Spice ephemeris time of frame
    :param universe_frame: frame of down, right, and direction vectors
    :param texture_maps: dict of texture map to use to draw planet. key is spice id, for instance 599 for Jupiter
                         or 501 for Io. value is loaded texture map -- a numpy array with shape (rows, cols, 3)

    :return: None, but a side effect is that the ellipsoids in question are drawn on the frame buffer

    Algorithm:
    * Ellpsoids to draw are texture_maps.keys()
    * Sort ellipsoid centers by distance
    * For each ellipsoid in distance order from far to near:
    *    Make a set of shaders that includes all ellipsoids except for this one
    *    use planet() to draw the ellipsoid
    """
    # * Ellpsoids to draw are texture_maps.keys()
    if extra_rots is None:
        extra_rots={}
    ellipsoid_spice_ids=list(texture_maps.keys())
    # * Sort ellipsoid centers by distance
    ellipsoid_distances=[vlength(spkezr(str(id),et,"IAU_"+bodc2n(id).upper(),"LT+S",str(view_spice_id))[0][:3]) for id in ellipsoid_spice_ids]
    pairs=list(zip(ellipsoid_distances,ellipsoid_spice_ids))
    pairs.sort(reverse=True)
    sorted_ids=[id for _,id in pairs]
    id_set=set(sorted_ids)
    # * For each ellipsoid in distance order from far to near:
    for id in sorted_ids:
        # *    Make a set of shaders that includes all ellipsoids except for this one
        shaders=id_set-{id}
        # *    use planet() to draw the ellipsoid
        planet(frame_buffer=frame_buffer,
               down_u=down_u,
               right_u=right_u,
               direction_u=direction_u,
               ellipsoid_spice_id=id,
               view_spice_id=view_spice_id,
               light_spice_id=light_spice_id,
               et=et,
               shadow_casters_spice_ids=shaders,
               universe_frame=universe_frame,
               texture_map=texture_maps[id],
               extra_rot=extra_rots[id] if id in extra_rots else 0)
