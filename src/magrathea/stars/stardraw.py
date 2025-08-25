"""
Draw stars in a star catalog

Created: 8/19/25
"""
import numpy as np
from kwanmath.gaussian import twoD_Gaussian
from kwanmath.interp import linterp
from kwanmath.vector import vnormalize

_DEFAULT_SIG_X=1.5
_DEFAULT_SIG_Y=1.0

def _draw_star(*,
              frame_buffer:np.ndarray,
              v_u:np.ndarray,
              color:np.ndarray,
              M_cu:np.ndarray,
              sig_x:float=_DEFAULT_SIG_X,
              sig_y:float=_DEFAULT_SIG_Y,
              theta:float=None
              ):
    """

    :param frame_buffer:
    :param v_u:
    :param color:
    :param right_u:
    :param down_u:
    :param direction_u:
    :param sig_x:
    :param sig_y:
    :return:
    """
    # Calculate position of star in camera frame
    v_c=M_cu @ v_u
    if v_c[2,0]<0.0:
        return
    xd_c=v_c[0,0]/v_c[2,0]
    yd_c=v_c[1,0]/v_c[2,0]
    # calculate pixel coordinate of centroid
    xp=linterp(-0.5,0,0.5,frame_buffer.shape[1],xd_c)
    yp=linterp(-0.5,0,0.5,frame_buffer.shape[0],yd_c)
    xpi=int(xp)
    xpf=xp-int(xp)
    ypi=int(yp)
    ypf=yp-int(yp)
    if theta is None:
        alpha=sig_x
        beta=sig_y
        rho=0.0
    else:
        c=np.cos(np.deg2rad(theta))
        s=np.sin(np.deg2rad(theta))
        alpha=np.sqrt(sig_x**2*c**2+sig_y**2*s**2)
        beta =np.sqrt(sig_x**2*s**2+sig_y**2*c**2)
        rho  =(sig_x**2-sig_y**2)*c*s/(alpha*beta)
    boxr_x=int(alpha*5)
    boxr_y=int(beta*5)
    xsize = frame_buffer.shape[1]
    ysize = frame_buffer.shape[0]
    if not (-boxr_x<=xpi<=xsize+boxr_x):
        return
    if not (-boxr_y<=ypi<=ysize+boxr_y):
        return
    box_xc=xpf+boxr_x
    box_yc=ypf+boxr_y
    y,x=np.mgrid[0:2*boxr_y,0:2*boxr_x]
    plane=twoD_Gaussian(x,y,
                     amplitude=1.0,xc=box_xc,yc=box_yc,
                     sigma_x=alpha,sigma_y=beta,
                     rho=rho,offset=0.0)

    star=plane[:,:,None]*color.reshape(-1)
    if False:
        star_frame=np.zeros((frame_buffer.shape[0]+4*boxr_y,frame_buffer.shape[1]+4*boxr_x,3))
        star_frame[ypi+boxr_y:ypi+3*boxr_y,xpi+boxr_x:xpi+3*boxr_x,:]=star
        frame_buffer[:,:,:]+=star_frame[2*boxr_y:star_frame.shape[0]-2*boxr_y,2*boxr_x:star_frame.shape[1]-2*boxr_x,:]
    else:
        # Clipped frame slice bounds
        left = max(0, xpi - boxr_x)
        right = min(xsize, xpi + boxr_x)
        top = max(0, ypi - boxr_y)
        bottom = min(ysize, ypi + boxr_y)

        # Corresponding offsets in the star array
        star_left = left - (xpi - boxr_x)
        star_right = star_left + (right - left)
        star_top = top - (ypi - boxr_y)
        star_bottom = star_top + (bottom - top)

        # Sub-star to assign
        sub_star = star[star_top:star_bottom, star_left:star_right, :]

        # Assign (use += for additive blending if needed)
        frame_buffer[top:bottom, left:right, :] += sub_star


def draw_stars(*,
               frame_buffer:np.ndarray,
               stars:list[tuple[np.ndarray,np.ndarray,...]],
               right_u:np.ndarray,
               down_u:np.ndarray,
               direction_u:np.ndarray,
               sig_x:float=_DEFAULT_SIG_X,
               sig_y:float=_DEFAULT_SIG_Y,
              ):
    """

    :param frame_buffer:
    :param stars:List of tuples:
       * v_u - unit vector pointing at star in universe frame
       * color - rgb color, each component in range [0,1]
       * other things like names etc are allowed but not used
    :param right_u: Right vector of camera in universe frame, including aspect ratio scaling
    :param down_u: Down vector of camera in universe frame
    :param direction_u: Direction vector of camera in universe frame, including field-of-view scaling
    :param sig_x:
    :param sig_y:
    :return:
    """
    M_uc=np.hstack((right_u,down_u,direction_u))
    M_cu=np.linalg.inv(M_uc)
    for v_u,color,*_ in stars:
        _draw_star(frame_buffer=frame_buffer,
                  v_u=v_u,
                  color=color,
                  M_cu=M_cu,
                  sig_x=sig_x,sig_y=sig_y)


def draw_sun(*,
               frame_buffer:np.ndarray,
               sun_u:np.ndarray,
               right_u:np.ndarray,
               down_u:np.ndarray,
               direction_u:np.ndarray,
               scale:float=1.0):
    """
    Draw sun as several Gaussians
    :param frame_buffer:
    :param sun_u: position of sun in camera-centered universe frame. For Voyager, use spkezr(10,et,univ_frame,"LT+S",-30-vgr)
    :param right_u: Right vector of camera in universe frame, including aspect ratio scaling
    :param down_u: Down vector of camera in universe frame
    :param direction_u: Direction vector of camera in universe frame, including field-of-view scaling
    """
    M_uc=np.hstack((right_u,down_u,direction_u))
    M_cu=np.linalg.inv(M_uc)
    v_u=vnormalize(sun_u)
    _draw_star(frame_buffer=frame_buffer,
               v_u=v_u,
               color=np.ones((3,1)),
               M_cu=M_cu,
               sig_x=20*scale,sig_y= 3*scale)
    _draw_star(frame_buffer=frame_buffer,
               v_u=v_u,
               color=np.ones((3,1)),
               M_cu=M_cu,
               sig_x= 3*scale,sig_y=20*scale)
    _draw_star(frame_buffer=frame_buffer,
               v_u=v_u,
               color=np.ones((3,1)),
               M_cu=M_cu,
               sig_x=10*scale,sig_y=2*scale,theta=45)
    _draw_star(frame_buffer=frame_buffer,
               v_u=v_u,
               color=np.ones((3,1)),
               M_cu=M_cu,
               sig_x=10*scale,sig_y=2*scale,theta=-45)
