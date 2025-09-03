"""
Describe purpose of this script here

Created: 8/28/25
"""
import numpy as np
from matplotlib import pyplot as plt

from magrathea.triangle.tridraw import tri_raster


def test_tri_raster():
    fb=np.zeros((100,100,3))
    a=14,27
    b=90,20
    c=17,88
    d=92,94
    tri_raster(fb,np.ones(3)*0.5,*a,*b,*c,combine=lambda a,b:a+b)
    tri_raster(fb,np.array([1,0,0])*0.5,*b,*d,*c,combine=lambda a,b:a+b)
    plt.imshow(fb)
    plt.show()