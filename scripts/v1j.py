"""
Describe purpose of this script here

Created: 8/19/25
"""
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from kwanmath.interp import linterp
from kwanmath.vector import vnormalize
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from spiceypy import furnsh, str2et, spkezr, etcal, sce2s, pxform

from magrathea import draw_planets, stage, draw_stars, load_stars, draw_sun
from magrathea.media.ffmpeg import ffmpeg
from magrathea.media.image import rebin_rgb
from magrathea.stage import double_stage
from magrathea.stars.stardraw import _DEFAULT_SIG_X,_DEFAULT_SIG_Y
from magrathea.triangle.mesh import Mesh
from magrathea.triangle.meshload import load3mf
from magrathea.triangle.tridraw import tri_raster

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

io_pos = np.array([
    [1180, 15.0132857264652, 212.613198489277],
    [1190, 33.6216038947996, 210.160808132507],
    [1200, 53.3116942790593, 209.826281780388],
    [1300, 297.314162960183, 197.094989237805],
    [1400, 591.492177179341, 181.155201550463],
    [2280, 395.440903839349, 368.068392577031],
    [2290, 388.953831327293, 356.413437580122],
    [2300, 383.730638635570, 345.487888842404],
    [2310, 377.856668490960, 336.184464154363],
    [2320, 371.554804227927, 324.686237575078],
    [2330, 366.045469235411, 315.141209486829],
    [2340, 360.837489313330, 303.885138042338],
    [2350, 354.037482444944, 292.449244203478],
    [2360, 347.423163411444, 282.210876845410],
    [2370, 342.779295043973, 270.272961194193],
    [2380, 336.877579625242, 259.231392321448],
    [2390, 330.769858463083, 248.958672436011],
    [2400, 325.092144930486, 237.768056683053],
    [2410, 317.870373792774, 228.653978412783],
    [2420, 312.414497812382, 218.748470085024],
    [2430, 305.766112216334, 202.587498558853],
    [2440, 299.786761280688, 192.047179138707],
    [2450, 293.361934032853, 179.663179994451],
    [2460, 287.488081870793, 165.476541005499],
    [2461, 287.657377949656, 167.364204187425],
    [2462, 288.457229762495, 174.181401167389],
    [2463, 286.346597435253, 161.295670250783],
    [2464, 286.080759066276, 159.853174951244],
    [2465, 284.189214768035, 158.421757835448],
    [2466, 284.720555072855, 156.662258613916],
    [2467, 285.442469001714, 161.392806991406],
    [2468, 285.299324952126, 159.185286453273],
    [2469, 286.168136586058, 159.753411009666],
    [2470, 287.140654626557, 169.845459580192],
    [2471, 291.580165118540, 171.836795333733],
    [2472, 285.959886827383, 177.744136042553],
    [2473, 287.589845615787, 185.178105885114],
    [2474, 286.393928064949, 187.231939245920],
    [2475, 287.269651297451, 185.115661804071],
    [2476, 289.405551379018, 195.251792156678],
    [2477, 288.824947634009, 186.089789524327],
    [2478, 289.409165153084, 189.202446880356],
    [2479, 287.987469559458, 191.978068376758],
    [2480, 291.951134452600, 193.619001771629],
    [2490, 293.498421890695, 187.214862489361],
    [2491, 291.275811820445, 190.813200742287],
    [2500, 293.091944159560, 186.742459350519],
])
io_a=np.logical_and(2280<=io_pos[:,0],io_pos[:,0]<=2465)
f_io_a_xd=np.poly1d(np.polyfit(io_pos[io_a,0],io_pos[io_a,1],1))
f_io_a_yd=np.poly1d(np.polyfit(io_pos[io_a,0],io_pos[io_a,2],1))

def f_io_xd(i_framenum):
    if i_framenum<=2465:
        return f_io_a_xd(i_framenum)


def f_io_yd(i_framenum):
    if i_framenum<=2465:
        return f_io_a_yd(i_framenum)


@dataclass
class Staging:
    pri_pos:np.ndarray
    sec_pos:np.ndarray
    pri_xpos:Callable[[int],float]=lambda i_frame:0
    pri_ypos:Callable[[int],float]=lambda i_frame:0
    sec_xpos:Callable[[int],float]=lambda i_frame:0
    sec_ypos:Callable[[int],float]=lambda i_frame:0
    fg_xpos:Callable[[int],float]=lambda i_frame:0
    fg_ypos:Callable[[int],float]=lambda i_frame:0
    fg_dist:Callable[[int],float]=lambda i_frame:20
    t:Callable[[int],float]=lambda i_frame:0




def main():
    univ_frame="ECLIPB1950"
    # begin literate_doc spice_furnsh literate_doc/Spice.ipynb
    vgr=1
    furnsh(f"data/spice/vgr{vgr}.tm")
    furnsh("data/spice/lsk/naif0012.tls")
    furnsh("data/spice/pck/pck00011.tpc")
    furnsh("data/spice/pck/jupiter_system2.tpc")
    # end literate_doc spice_furnsh
    scale=2
    n_unscaled_rows=1080
    n_unscaled_cols=1440
    n_rows=n_unscaled_rows*scale
    n_cols=n_unscaled_cols*scale
    texture_maps = {599: (1*plt.imread("data/textures/JupiterMap.png")).astype(np.float64),
                    501: (1*plt.imread("data/textures/IoMap.png")).astype(np.float64),
                    502: (1*plt.imread("data/textures/EuropaMap.png")).astype(np.float64),
                    503: (1*plt.imread("data/textures/GanymedeMap.png")).astype(np.float64),
                    504: (1*plt.imread("data/textures/CallistoMap.png")).astype(np.float64),
                    }
    stars=load_stars(frame=univ_frame)
    sc_mesh:Mesh=load3mf("data/output/mesh/voyager.3mf")
    extra_rots = {599: -16}
    et_ca=str2et(cal_ca)
    # from frame 1212, which includes Jupiter, Io in foreground, and one more moon (Europa?) in the background
    for frame_number in range(1,4941+1):
    #for frame_number in range(1212,1213):
        et=float(f_et(frame_number)) #1979-03-04 20:28:31.788 ET, J-15:36:54.211
        print(f"{frame_number:4d}, {et:.6f}, {etcal(et)}, {sce2s(-31,et)}")
        # Copied from Stage HudMatrix. That is a camera-to-universe transformation
        # but in the transposed row-vector form that POV-Ray uses. Put the data here exactly as-is,
        # then chunk out and de-transpose it with code.
        # begin literate_doc spkezr literate_doc/Spice.ipynb
        # Get position of planet relative to spacecraft, with LT+S geometric correction. This shows
        # where Jupiter is at the time that light leaves it to arrive at the spacecraft at the requested time.
        # It also shows stellar aberration due to relative motion of the objects. This results in the best
        # available position of where Jupiter *appears* to be from the spacecraft
        jupiter_state,_=spkezr("599",et,univ_frame,"LT+S",str(-30-vgr))
        jupiter_pos=jupiter_state[:3].reshape(-1,1)
        # Same with Io, Ganymede, and Callisto, since we use all of these for staging
        io_state,_=spkezr("501",et,univ_frame,"LT+S",str(-30-vgr))
        io_pos=io_state[:3].reshape(-1,1)
        ganymede_state,_=spkezr("503",et,univ_frame,"LT+S",str(-30-vgr))
        ganymede_pos=ganymede_state[:3].reshape(-1,1)
        callisto_state,_=spkezr("504",et,univ_frame,"LT+S",str(-30-vgr))
        callisto_pos=callisto_state[:3].reshape(-1,1)
        # Same with the Sun. It's far enough away that LT+S might actually make a pixel's worth of difference.
        sun_state,_=spkezr("10",et,univ_frame,"LT+S",str(-30-vgr))
        sun_pos=sun_state[:3].reshape(-1,1)
        # end literate_doc spkezr
        frame_stage=None
        def stage1(f0,f1,actor,this_f_xd=f_xd,this_f_yd=f_yd):
            return stage(camera_ru=np.array([[0.0], [0.0], [0.0]]),
                                actor_ru=actor,
                                sky_vec=np.array([[0.0], [0.0], [1.0]]),
                                right_scale=4.0 / 3.0,
                                angle=18.0,
                                x_d=this_f_xd(frame_number),
                                y_d=this_f_yd(frame_number)
                              )
        def stage2(f0,f1,actor0,actor1, *,
                   f0_xd=f_xd,f0_yd=f_yd,
                   f1_xd=f_xd,f1_yd=f_yd):
            return double_stage(camera_ru=np.array([[0.0], [0.0], [0.0]]),
                               actor_ru0=actor0, x0_d=f0_xd(frame_number), y0_d=f0_yd(frame_number),
                               actor_ru1=actor1, x1_d=f1_xd(frame_number), y1_d=f1_yd(frame_number),
                               t=linterp(f0, 0.0, f1, 1.0, frame_number),
                               sky_vec=np.array([[0.0], [0.0], [1.0]]), right_scale=4 / 3, angle=18
                               )
        stage_table=[
            (0,2185,jupiter_pos,f_xd,f_yd,None,None,None,lambda i_frame:0),
            (2185,2279,)
        ]
        if frame_number<=2185:
            frame_stage=stage1(0,2185,jupiter_pos)

        elif frame_number<=2279:
            frame_stage=stage2(2185,2279,jupiter_pos,io_pos)#,    f1_xd=f_io_xd,    f1_yd=f_io_yd)
        elif frame_number<=2872:
            frame_stage=stage1(2279,2872,            io_pos)#,this_f_xd=f_io_xd,this_f_yd=f_io_yd)
        elif frame_number<=2966:
            frame_stage=stage2(2873,2966,io_pos,ganymede_pos)
        elif frame_number<=3372:
            frame_stage=stage1(2967,3372,ganymede_pos)
        elif frame_number<=3466:
            frame_stage=stage2(3373,3466,ganymede_pos,jupiter_pos)
        elif frame_number<=3780:
            frame_stage=stage1(3467,3780,jupiter_pos)
        elif frame_number<=3873:
            frame_stage=stage2(3781,3873,jupiter_pos,callisto_pos)
        elif frame_number<=4279:
            frame_stage=stage1(3874,4279,callisto_pos)
        elif frame_number<=4371:
            frame_stage=stage2(4280,4371,callisto_pos,jupiter_pos)
        else:
            frame_stage=stage1(4372,4941,jupiter_pos)
        frame_buffer=np.zeros([n_rows,n_cols,3],dtype=np.float64)
        draw_stars(frame_buffer=frame_buffer,stars=stars,
                   down_u=frame_stage.down_u,
                   right_u=frame_stage.right_u,
                   direction_u=frame_stage.direction_u,
                   sig_x=scale*_DEFAULT_SIG_X,
                   sig_y=scale * _DEFAULT_SIG_Y,

                   )
        draw_sun(frame_buffer=frame_buffer,sun_u=sun_pos,
                 down_u=frame_stage.down_u,
                 right_u=frame_stage.right_u,
                 direction_u=frame_stage.direction_u,
                 scale=scale
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
                     use_c=True)
        M_ub=pxform(f"VG{vgr}_SC_BUS",univ_frame,et)
        M_uc=np.hstack((frame_stage.right_u,frame_stage.down_u,frame_stage.direction_u))
        M_cu=np.linalg.inv(M_uc)
        lhat_u=vnormalize(sun_pos)
        sc_mesh.rasterize(frame_buffer=frame_buffer,M_ub=M_ub,M_cu=M_cu,T_c=np.array([[0.0],[0.0],[20.0]]),lhat_u=lhat_u)
        sm_frame_buffer=rebin_rgb(frame_buffer,(n_unscaled_rows,n_unscaled_cols,3))
        plt.imsave(f"data/output/v1j/frame_{frame_number:04d}.png",np.clip(frame_buffer,0.0,1.0))
        plt.imsave(f"data/output/v1j_small/frame_{frame_number:04d}.png",np.clip(sm_frame_buffer,0.0,1.0))
        if frame_number%10==0:
            plt.clf()
            plt.imshow(sm_frame_buffer)
            plt.title(f"Frame {frame_number}")
            plt.pause(0.01)
    ffmpeg("data/output/v1j_small/frame_%04d.png","data/output/v1j.mkv")


if __name__ == "__main__":
    main()
