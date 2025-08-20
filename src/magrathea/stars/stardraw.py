"""
Draw stars in a star catalog

Created: 8/19/25
"""
import numpy as np
from kwanmath.gaussian import twoD_Gaussian
from kwanmath.interp import linterp


def draw_star(*,
              frame_buffer:np.ndarray,
              v_u:np.ndarray,
              color:np.ndarray,
              right_u:np.ndarray,
              down_u:np.ndarray,
              direction_u:np.ndarray,
              sig_x:float=3.0,
              sig_y:float=3.0,
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
    M_uc=np.hstack((right_u,down_u,direction_u))
    M_cu=M_uc.T
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
    boxr_x=int(sig_x*5)
    boxr_y=int(sig_y*5)
    if not (-boxr_x<=xd_c<=frame_buffer.shape[1]+boxr_x):
        return
    if not (-boxr_y<=yd_c<=frame_buffer.shape[0]+boxr_y):
        return
    box_xc=xpf+boxr_x
    box_yc=ypf+boxr_y
    y,x=np.mgrid[0:2*boxr_y,0:2*boxr_x]
    plane=twoD_Gaussian(x,y,
                      amplitude=1.0,xc=box_xc,yc=box_yc,
                      sigma_x=sig_x,sigma_y=sig_y,
                      rho=0.0,offset=0.0)
    star=plane[:,:,None]*color.reshape(-1)
    frame_buffer[xpi-boxr_y:xpi+boxr_y,ypi-boxr_x:ypi+boxr_x,:]=star


def draw_stars():
    pass
