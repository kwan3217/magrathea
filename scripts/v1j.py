"""
Describe purpose of this script here

Created: 8/19/25
"""
from dataclasses import dataclass

import numpy as np
from kwanmath.interp import linterp
from kwanmath.matrix import point_toward
from kwanmath.vector import vnormalize
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from spiceypy import furnsh, str2et, spkezr

from magrathea import planets

# Closest approach on calendar
cal_ca="1979-03-05 12:05:26 TDB"
rubber_clock=np.array([
    [1238,	-657299160.0     ],
    [1346,	-657292812.046332],
    [1387,	-657290822.175032],
    [1388,	-657290343.397684],
    [1389,	-657290284.620335],
    [1390,	-657290225.842986],
    [1391,	-657290167.065637],
    [1701,	-657272606.672883],
    [2701,	-657220199.519541],
    [3756,	-657159019.772765],
    [4515,	-657115048.349255],
    [4797,	-657098669.14052 ]]
)
f_et=interp1d(rubber_clock[:, 0], rubber_clock[:, 1], kind='linear', fill_value='extrapolate')

jupiter_pos=np.array([
   [ 330,	218.086650516856,	229.128544196091],
   [ 430,	207.991758097495,	223.355790534115],
   [ 530,	199.897673147538,	214.631523301627],
   [ 630,	197.925496001986,	207.942872090036],
   [ 670,	199.580115082222,	206.025989560958],
   [ 700,	194.313484215603,	201.72075979344 ],
   [ 717,	185.640994657917,	198.365917743208],
   [ 800,	178.05830242027 ,	191.462338009167],
   [ 894,	195.999814421613,	194.361074695563],
   [ 900,	196.543810731952,	194.39902701721 ],
   [ 979,	213.307043783177,	197.025811555916],
   [1000,	217.421302205295,	198.885076811364],
   [1100,	237.885670711657,	203.281969384618],
   [1200,	258.499711844441,	206.641237640298],
   [1238,	268.172951591134,	208.74939357576 ],
   [1300,	279.278662184253,	209.835532426236],
   [1346,	289.821192681776,	213.05068735074 ],
   [1387,	297.306934827983,	214.165522399942],
   [1400,	299.053536481189,	215.09862107381 ],
   [1500,	321.712009715949,	220.01519533549 ],
   [1600,	340.127919393118,	222.037790289735],
   [1700,	353.636735817922,	227.268348575425],
   [1701,	359.11554427203 ,	226.675356969349],
   [1800,	371.40406732944 ,	234.33982446882 ],
   [1900,	374.125967649316,	233.957801093284],
   [2000,	338.56836422701 ,	252.934236465958],
   [3756,	366.960729754548,	208.896668393555],
   [4515,	356.986465711134,	213.815450059114],
   [4797,	333.791771516755,	226.936599745126]]
)
f_xp=interp1d(jupiter_pos[:,0],jupiter_pos[:,1],kind='linear', fill_value='extrapolate')
f_yp=interp1d(jupiter_pos[:,0],jupiter_pos[:,2],kind='linear', fill_value='extrapolate')
f_xd=lambda fn:linterp(0,-0.5,640,0.5,f_xp(fn))
f_yd=lambda fn:linterp(0,-0.5,480,0.5,f_yp(fn))

@dataclass
class LocalStageResult:
    stage_right:np.ndarray
    stage_down:np.ndarray
    stage_out:np.ndarray
    location:np.ndarray
    look_at:np.ndarray
    cam_sky:np.ndarray
    cam_right:np.ndarray
    cam_angle:float
    direction_scale:float


def local_stage(*,
          camera_ru:np.ndarray,
          actor_ru:np.ndarray,
          sky_vec:np.ndarray,
          right_scale:float,
          angle:float,
          x_d:float,
          y_d:float)->LocalStageResult:
    # Calculate direction from angle and aspect ratio
    direction_scale=0.5*right_scale/np.tan(np.deg2rad(angle)/2)
    cam_angle=angle
    cam_right=np.array([[right_scale],
                        [0.0],
                        [0.0]])
    x=np.array([[1.0],[0.0],[0.0]])
    y=np.array([[0.0],[1.0],[0.0]])
    z=np.array([[0.0],[0.0],[1.0]])
    #PrintNumber("DirectionScale: ",DirectionScale)
    # Create actor vector in stage frame
    z_d=1
    r_d=np.array([[x_d],
                  [y_d],
                  [z_d]])
    #PrintVector("r_d: ",r_d)
    # Transform actor vector into camera orthonomral frame
    r_n=r_d*np.array([[right_scale],[1],[direction_scale]])
    #PrintVector("r_n: ",r_n)
    # Implement Point-Toward. We have R=[p_r, s_r, u_r] in reference (universe) space, and
    p_r=vnormalize(actor_ru-camera_ru)
    #PrintVector("Pr: ",Pr)
    p_b=vnormalize(r_n)
    #PrintVector("Pb: ",Pb)
    t_r=vnormalize(sky_vec)
    #PrintVector("Tr: ",Tr)
    t_b=-y
    #PrintVector("Tb: ",Tb)
    M_rb=point_toward(p_r=p_r,p_b=p_b,t_r=t_r,t_b=t_b)
    #PrintMatrix("M_rb: ",M_rb)
    #// Stage vectors in camera universe space. These are appropriate for placing foreground actors. They are all unit
    #// length so you will have to take into account z distance, direction, and aspect to place objects.
    stage_right=M_rb @ x
    #local Result[0]=StageRight;
    stage_down=M_rb @ y
    #local Result[1]=StageDown;
    stage_out=M_rb @ z
    #local Result[2]=StageOut;
    #// Assign camera variables
    location=camera_ru
    #local Result[3]=Location;
    look_at=location+stage_out
    #local Result[4]=LookAt;
    cam_sky=vnormalize(sky_vec)
    #local Result[5]=CamSky;
    result=LocalStageResult(stage_right=stage_right,
                            stage_down=stage_down,
                            stage_out=stage_out,
                            location=location,
                            look_at=look_at,
                            cam_sky=cam_sky,
                            cam_right=cam_right,
                            cam_angle=cam_angle,
                            direction_scale=direction_scale)
    return result

@dataclass
class StageResult:
    right_u:np.ndarray
    down_u:np.ndarray
    direction_u:np.ndarray


def stage(*,
          camera_ru:np.ndarray,
          actor_ru:np.ndarray,
          sky_vec:np.ndarray,
          right_scale:float,
          angle:float,
          x_d:float,
          y_d:float)->StageResult:
    this_local_stage=local_stage(
        camera_ru=camera_ru,
        actor_ru=actor_ru,
        sky_vec=sky_vec,
        right_scale=right_scale,
        angle=angle,
        x_d=x_d,
        y_d=y_d
    )
    # Calculate direction from angle and aspect ratio
    direction_scale=this_local_stage.direction_scale
    cam_angle=this_local_stage.cam_angle
    cam_right=this_local_stage.cam_right
    stage_right=this_local_stage.stage_right
    stage_down=this_local_stage.stage_down
    stage_out=this_local_stage.stage_out
    #PrintVector(" StageRight: ",StageRight)
    #PrintVector(" StageDown:  ",StageDown )
    #PrintVector(" StageOut:   ",StageOut  )
    #PrintMatrix("M: ",M3b1b(StageRight,StageDown,StageOut))
    # Assign camera variables
    location=this_local_stage.location
    look_at=this_local_stage.look_at
    cam_sky=this_local_stage.cam_sky
    # Transformation appropriate for HUD. This properly projects things in the plane z=DirectionScale
    # to the screen. The top edge is at y=-0.5, bottom at y=+0.5, left at x=-CamRight*0.5, right at x=+CamRight*0.5
    # Note that this is uniform in the XY plane, so it won't distort text etc.
    # Note that POV-Ray convention looks like a transpose of my convention so
    #  M=[ M00 M01 M02 Tx]
    #    [ M10 M11 M12 Ty]
    #    [ M20 M21 M22 Tz]
    #    [   0   0   0  1]
    # is represented as:
    # transform{matrix <M00,M10,M20,
    #                   M01,M11,M21,
    #                   M02,M12,M22,
    #                   Tx ,Ty ,Tz  >}
    # Since we aren't in POV-Ray any more, we make a 4x4 matrix like above
    hud_matrix=np.vstack((np.hstack((stage_right,stage_down,stage_out*direction_scale,location)),
                          np.array([0.0,0.0,0.0,1.0])))
    return StageResult(right_u=stage_right*right_scale,down_u=stage_down,direction_u=stage_out*direction_scale)


def main():
    univ_frame="ECLIPB1950"
    vgr=1
    furnsh(f"data/spice/vgr{vgr}.tm")
    furnsh("data/spice/lsk/naif0012.tls")
    furnsh("data/spice/pck/pck00011.tpc")
    furnsh("data/spice/pck/jupiter_system2.tpc")
    texture_maps = {599: plt.imread("data/textures/JupiterMap.png"),
                    501: plt.imread("data/textures/IoMap.png"),
                    502: plt.imread("data/textures/EuropaMap.png"),
                    503: plt.imread("data/textures/GanymedeMap.png"),
                    504: plt.imread("data/textures/CallistoMap.png")}
    extra_rots = {599: -16}
    et_ca=str2et(cal_ca)
    # from frame 1212, which includes Jupiter, Io in foreground, and one more moon (Europa?) in the background
    for frame_number in range(1210,1220):
        print(frame_number)
        et=float(f_et(frame_number)) #1979-03-04 20:28:31.788 ET, J-15:36:54.211
        # Copied from Stage HudMatrix. That is a camera-to-universe transformation
        # but in the transposed row-vector form that POV-Ray uses. Put the data here exactly as-is,
        # then chunk out and de-transpose it with code.
        jupiter_state,_=spkezr("599",et,univ_frame,"LT+S",str(-30-vgr))
        jupiter_pos=jupiter_state[:3].reshape(-1,1)
        if frame_number<=2185:
            frame_stage=stage(camera_ru=np.array([[0.0],[0.0],[0.0]]),
                                             actor_ru=jupiter_pos,
                                             sky_vec=np.array([[0.0],[0.0],[1.0]]),
                                             right_scale=4.0/3.0,
                                             angle=18.0,
                                             x_d=f_xd(frame_number),
                                             y_d=f_yd(frame_number)
                                             )
        frame_buffer=np.zeros([1080,1440,3])
        planets(frame_buffer=frame_buffer,
                down_u=frame_stage.down_u,
                right_u=frame_stage.right_u,
                direction_u=frame_stage.direction_u,
                view_spice_id=-31,
                et=et,
                universe_frame=univ_frame,
                texture_maps=texture_maps,
                extra_rots=extra_rots)
        #plt.clf()
        #plt.imshow(frame_buffer)
        #plt.title(f"Frame {frame_number}")
        #plt.pause(0.01)
    #plt.show()


if __name__ == "__main__":
    main()
