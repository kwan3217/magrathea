"""
Describe purpose of this script here

Created: 8/19/25
"""
import numpy as np
from matplotlib import pyplot as plt
from spiceypy import furnsh

from magrathea import planets


def main():
    furnsh("data/spice/vgr1.tm")
    furnsh("data/spice/lsk/naif0012.tls")
    furnsh("data/spice/pck/pck00011.tpc")
    furnsh("data/spice/pck/jupiter_system2.tpc")
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
    planets(frame_buffer=frame_buffer,
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


if __name__ == "__main__":
    main()
