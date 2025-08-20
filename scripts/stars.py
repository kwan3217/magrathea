"""
Describe purpose of this script here

Created: 8/20/25
"""
import numpy as np
from matplotlib import pyplot as plt
from spiceypy import furnsh

from magrathea import load_stars, draw_stars


def main():
    univ_frame="ECLIPB1950"
    vgr=1
    furnsh(f"data/spice/vgr{vgr}.tm")
    furnsh("data/spice/lsk/naif0012.tls")
    furnsh("data/spice/pck/pck00011.tpc")
    furnsh("data/spice/pck/jupiter_system2.tpc")
    stars=load_stars(frame=univ_frame)
    print(len(stars))
    frame_buffer = np.zeros([1080, 1440, 3])
    draw_stars(frame_buffer=frame_buffer,
              stars=stars,
              right_u=np.array([[1.0],[0.0],[0.0]])*4/3,
              down_u=np.array([[0.0],[1.0],[0.0]]),
              direction_u=np.array([[0.0],[0.0],[1.0]])
              )
    plt.clf()
    plt.imshow(frame_buffer)
    plt.show()


if __name__ == "__main__":
    main()
