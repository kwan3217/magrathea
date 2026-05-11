"""
Describe purpose of this script here

Created: 8/18/25
"""
import numpy as np
import matplotlib.pyplot as plt
import pytest
from spiceypy import furnsh



@pytest.fixture(autouse=True,scope="session")
def furnish():
    furnsh("data/spice/vgr1.tm")
    furnsh("data/spice/lsk/naif0012.tls")
    furnsh("data/spice/pck/pck00011.tpc")
    furnsh("data/spice/pck/jupiter_system2.tpc")


def test_planet():
    frame_buffer=np.zeros([1080,1440,3])
    draw_planet(frame_buffer=frame_buffer,
                down_u=np.array([[1.0],[0.0],[0]]),
                right_u=np.array([[0.0],[4.0/3.0],[0]]),
                direction_u=np.array([[0.0],[0.0],[1.0]]),
                ellipsoid_spice_id=599,
                view_spice_id=-31,
                light_spice_id=10,
                et=-1000,
                texture_map=plt.imread("data/textures/JupiterMap.png"),
                r_viewpoint_b=np.array([[0.0],[0.0],[-3e5]]),
                M_bu=np.identity(3),
                r_light_b=np.array([[1e8],[0.0],[0.0]]))
    plt.imshow(frame_buffer)
    plt.show()


def test_planets():
    # from frame 1212, which includes Jupiter, Io in foreground, and one more moon (Europa?) in the background
    et=-657300688.211068 #1979-03-04 20:28:31.788 ET, J-15:36:54.211
    univ_frame="ECLIPB1950"
    # Copied from Stage HudMatrix. That is a camera-to-universe transformation
    # but in the transposed row-vector form that POV-Ray uses. Put the data here exactly as-is,
    # then chunk out and de-transpose it with code.
    hud_matrix=np.array([[ 0.731019, 0.682357,-0.000059],
                         [-0.001443, 0.001459,-0.999998],
                         [-2.872148, 3.076976, 0.008634],
                         [ 0.000000, 0.000000, 0.000000]])
    right_u=hud_matrix[0,None,:].T*4/3
    down_u=hud_matrix[1,None,:].T
    direction_u=hud_matrix[2,None,:].T
    frame_buffer=np.zeros([1080,1440,3])
    texture_maps={599:plt.imread("data/textures/JupiterMap.png"),
                  501:plt.imread("data/textures/IoMap.png"),
                  502:plt.imread("data/textures/EuropaMap.png"),
                  503:plt.imread("data/textures/GanymedeMap.png"),
                  504:plt.imread("data/textures/CallistoMap.png")}
    extra_rots={599:-16}
    draw_planets(frame_buffer=frame_buffer,
                 down_u=down_u,
                 right_u=right_u,
                 direction_u=direction_u,
                 view_spice_id=-31,
                 et=et,
                 universe_frame=univ_frame,
                 texture_maps=texture_maps,
                 extra_rots=extra_rots)
    plt.imshow(frame_buffer)
    plt.show()


