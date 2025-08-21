"""
Describe purpose of this script here

Created: 8/19/25
"""

import numpy as np
from kwanmath.interp import linterp
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from spiceypy import furnsh, str2et, spkezr

from magrathea import draw_planets, stage, draw_stars, load_stars

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


def main():
    univ_frame="ECLIPB1950"
    vgr=1
    furnsh(f"data/spice/vgr{vgr}.tm")
    furnsh("data/spice/lsk/naif0012.tls")
    furnsh("data/spice/pck/pck00011.tpc")
    furnsh("data/spice/pck/jupiter_system2.tpc")
    n_rows=480
    n_cols=640
    texture_maps = {599: (1*plt.imread("data/textures/JupiterMap.png")).astype(np.float64),
                    501: (1*plt.imread("data/textures/IoMap.png")).astype(np.float64),
                    502: (1*plt.imread("data/textures/EuropaMap.png")).astype(np.float64),
                    503: (1*plt.imread("data/textures/GanymedeMap.png")).astype(np.float64),
                    504: (1*plt.imread("data/textures/CallistoMap.png")).astype(np.float64),
                    }
    stars=load_stars(frame=univ_frame)
    extra_rots = {599: -16}
    et_ca=str2et(cal_ca)
    # from frame 1212, which includes Jupiter, Io in foreground, and one more moon (Europa?) in the background
    #for frame_number in range(330,2185):
    for frame_number in range(1210,1220):
        print(frame_number)
        et=float(f_et(frame_number)) #1979-03-04 20:28:31.788 ET, J-15:36:54.211
        # Copied from Stage HudMatrix. That is a camera-to-universe transformation
        # but in the transposed row-vector form that POV-Ray uses. Put the data here exactly as-is,
        # then chunk out and de-transpose it with code.
        jupiter_state,_=spkezr("599",et,univ_frame,"LT+S",str(-30-vgr))
        jupiter_pos=jupiter_state[:3].reshape(-1,1)
        if frame_number<=2185:
            frame_stage= stage(camera_ru=np.array([[0.0], [0.0], [0.0]]),
                               actor_ru=jupiter_pos,
                               sky_vec=np.array([[0.0],[0.0],[1.0]]),
                               right_scale=4.0/3.0,
                               angle=18.0,
                               x_d=f_xd(frame_number),
                               y_d=f_yd(frame_number)
                               )
        frame_buffer=np.zeros([n_rows,n_cols,3],dtype=np.float64)
        draw_stars(frame_buffer=frame_buffer,stars=stars,
                   down_u=frame_stage.down_u,
                   right_u=frame_stage.right_u,
                   direction_u=frame_stage.direction_u
                   )
        draw_planets(frame_buffer=frame_buffer,
                     down_u=frame_stage.down_u,
                     right_u=frame_stage.right_u,
                     direction_u=frame_stage.direction_u,
                     view_spice_id=-31,
                     et=et,
                     universe_frame=univ_frame,
                     texture_maps=texture_maps,
                     extra_rots=extra_rots,
                     use_c=False)
        plt.imsave(f"data/output/v1j/frame_{frame_number:04d}.png",np.clip(frame_buffer,0.0,1.0))
        plt.clf()
        plt.imshow(frame_buffer)
        plt.title(f"Frame {frame_number}")
        plt.pause(0.01)
    plt.show()


if __name__ == "__main__":
    main()
