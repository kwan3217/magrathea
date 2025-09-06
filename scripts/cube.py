"""
Render a 3D cube

Created: 9/2/25
"""
import numpy as np
from kwanmath.interp import linterp
from kwanmath.matrix import rot_x
from magrathea.triangle.tridraw_cy import py_tris_draw
from matplotlib import pyplot as plt

from magrathea.triangle.meshload import load3mf
from magrathea.triangle.tridraw import tri_raster, tri_raster_grok

resistor_color_code=np.array([[0.25,0.25,0.25],
                              [0.5,0.2,0.0],
                              [1.0,0.0,0.0],
                              [1.0,0.5,0.0],
                              [1.0,1.0,0.0],
                              [0.0,1.0,0.0],
                              [0.0,0.0,1.0],
                              [0.5,0.0,1.0],
                              [0.5,0.5,0.5],
                              [1.0,1.0,1.0]])

def main():
    if False:
        mesh=load3mf("data/output/mesh/cube.3mf")
        z_c=3
        mesh.tricolors = resistor_color_code[
            np.arange(mesh.tricolors.shape[0], dtype=np.int32) % resistor_color_code.shape[0], :]
    else:
        mesh=load3mf("data/output/mesh/voyager.3mf")
        z_c=20
    verbose=False
    print(mesh)
    thetas=np.arange(63)/10
    for i_theta,theta in enumerate(thetas):
        c=np.cos(theta)
        s=np.sin(theta)
        M_ub=rot_x(theta)
        frame_buffer = np.zeros((1000, 1000, 3))
        frame_buffer2 = np.zeros((1000, 1000, 3))
        tris_screen, tricolors_screen = mesh.shade_geometry(M_ub=M_ub,
                                                            M_cu=np.eye(3),
                                                            T_c=np.array([[0], [0], [z_c]]),
                                                            lhat_u=np.array([[0], [0], [-1]]), diffuse=0.9, ambient=0.1,
                                                            w=frame_buffer.shape[1], h=frame_buffer.shape[0])
        #py_tris_draw(frame_buffer,tris_screen,tricolors_screen)
        for tri, tricolor in zip(tris_screen,tricolors_screen):
            tri_raster(frame_buffer, tricolor, tri[0,0], tri[1,0], tri[0,1], tri[1,1], tri[0,2], tri[1,2])
            tri_raster_grok(frame_buffer2, tricolor, tri[0,0], tri[1,0], tri[0,1], tri[1,1], tri[0,2], tri[1,2])
        if verbose:
            plt.clf()
            plt.imshow(frame_buffer)
            plt.title(f"{i_theta}: {theta}")
            plt.pause(0.1)
        #break
    if verbose:
        plt.show()


if __name__ == "__main__":
    main()
