"""
Render a 3D cube

Created: 9/2/25
"""
import numpy as np
from kwanmath.interp import linterp
from kwanmath.matrix import rot_x
from matplotlib import pyplot as plt

from magrathea.triangle.meshload import load3mf
from magrathea.triangle.tridraw import tri_raster

resistor_color_code=np.array([[0.25,0.25,0.25],
                              [0.5,0.2,0.0],
                              [1.0,0.0,0.0],
                              [1.0,0.5,0.0],
                              [1.0,1.0,0.0],
                              [0.0,1.0,0.0],
                              [0.0,0.0,1.0],
                              [0.5,0.0,1.0],
                              [0.5,0.5,0.5],
                              [1.0,1.0,1.0]]).T

def main():
    cube=load3mf("data/output/mesh/cube.3mf")
    print(cube)
    cube.tricolors=resistor_color_code[:,np.arange(cube.tricolors.shape[1],dtype=np.int32)%resistor_color_code.shape[1]]
    for theta in np.arange(63)/10:
        c=np.cos(theta)
        s=np.sin(theta)
        M_ub=rot_x(theta)
        frame_buffer = np.zeros((1000, 1000, 3))
        tris_screen, tricolors_screen = cube.shade_geometry(M_ub=M_ub,
                                                            M_cu=np.eye(3),
                                                            T_c=np.array([[0], [0], [3]]),
                                                            lhat_u=np.array([[0], [0], [-1]]), diffuse=0.9, ambient=0.1,
                                                            w=frame_buffer.shape[1], h=frame_buffer.shape[0])
        for tri, tricolor in zip(tris_screen,tricolors_screen.T):
            tri_raster(frame_buffer, tricolor, tri[0,0], tri[1,0], tri[0,1], tri[1,1], tri[0,2], tri[1,2])
        plt.clf()
        plt.imshow(frame_buffer)
        plt.pause(0.1)
    plt.show()


if __name__ == "__main__":
    main()
