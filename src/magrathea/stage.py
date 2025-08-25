"""
Describe purpose of this script here

Created: 8/19/25
"""
from dataclasses import dataclass

import numpy as np
from kwanmath.matrix import point_toward, slerp
from kwanmath.vector import vnormalize


def main():
    pass


if __name__ == "__main__":
    main()


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
    direction_scale:float


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
    return StageResult(right_u=stage_right*right_scale,down_u=stage_down,direction_u=stage_out*direction_scale,direction_scale=direction_scale)


def double_stage(*,
        camera_ru: np.ndarray,
        actor_ru0: np.ndarray, x0_d:float, y0_d:float,
        actor_ru1: np.ndarray, x1_d:float, y1_d:float,
        t:float,
        sky_vec: np.ndarray,
        right_scale: float,
        angle: float
):
    # Primary stage
    stage0=local_stage(camera_ru=camera_ru,actor_ru=actor_ru0, sky_vec=sky_vec, right_scale=right_scale, angle=angle, x_d=x0_d,y_d=y0_d)
    M0=np.hstack((vnormalize(stage0.stage_right),vnormalize(stage0.stage_down),vnormalize(stage0.stage_out)))
    print(f"{M0=}")
    # Secondary stage
    stage1=local_stage(camera_ru=camera_ru,actor_ru=actor_ru1, sky_vec=sky_vec, right_scale=right_scale, angle=angle, x_d=x1_d,y_d=y1_d)
    M1=np.hstack((vnormalize(stage1.stage_right),vnormalize(stage1.stage_down),vnormalize(stage1.stage_out)))
    # inTerpolated stage (t for parameter $t$)
    MT=slerp(M0,M1,t)
    staget_right=MT[:,None,0]
    staget_down =MT[:,None,1]
    staget_out  =MT[:,None,2]
    """
    # Camera vectors, follows interpolation
    location=camera_ru
    #declare LookAt=Location+StageTOut;
    #declare CamSky=vnormalize(-StageTDown);
    // Foreground Stage vectors, follows stage 0
    #declare StageRight=Stage0Right;
    #declare StageDown =Stage0Down;
    #declare StageOut  =Stage0Out;
    // Camera parameters, constant between frames so use stage 0. Note that angle etc might change over time,
    // but will not change between stage 0 and stage 1. Any angle etc change will occur to both stages
    // in lockstep, so it's only specified once.
    #declare DirectionScale=Stage0[8].x;
    #declare CamAngle=Stage0[7].x;
    #declare CamRight=Stage0[6];
    // HUD Matrix, follow interpolation
    #declare HudMatrix=transform{
      MatrixVerbose("DoubleStage HudMatrix: ",
              StageTRight.x,StageTRight.y,StageTRight.z,
              StageTDown.x,StageTDown.y,StageTDown.z
              StageTOut.x*DirectionScale,StageTOut.y*DirectionScale,StageTOut.z*DirectionScale,
              Location.x,Location.y,Location.z)
    };
    """
    return StageResult(right_u=staget_right * right_scale,
                       down_u=staget_down,
                       direction_u=staget_out * stage0.direction_scale,direction_scale=stage0.direction_scale)


