"""
Load a triangle mesh

Created: 8/28/25
"""
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import numpy as np


class RequiredSectionMissingError(LookupError):
    pass


def parse_html_color(color:str):
    return np.array((int(color[1:3],16),int(color[3:5],16),int(color[5:7],16))).reshape(-1,1)/255


class Mesh:
    def __init__(self,infn:str):
        self.infn=infn
        self.load3mf()
        self.colors=None
        self.vertices=None
        self.triangles=None
        self.tricolors=None
    def load3mf(self):
        with ZipFile(self.infn, "r") as zip:
            with zip.open("3D/3dmodel.model") as inf:
                content=inf.read().decode('utf8')
        root=ET.fromstring(content)
        namespaces = {
            '3mf': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02',
            'm': 'http://schemas.microsoft.com/3dmanufacturing/material/2015/02',
            'p': 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06',
            'b': 'http://schemas.microsoft.com/3dmanufacturing/beamlattice/2017/02',
            's': 'http://schemas.microsoft.com/3dmanufacturing/slice/2015/07'
        }
        colorgroups=root.findall('.//3mf:resources/m:colorgroup',namespaces)
        if not colorgroups:
            raise RequiredSectionMissingError("No section matching './/3mf:resources/3mf:colorgroup'")
        colorgroup=colorgroups[0]
        colors=np.hstack([parse_html_color(color.attrib["color"]) for color in colorgroup])
        print(colors.shape)
        meshes=root.findall('.//3mf:resources/3mf:object/3mf:mesh',namespaces)
        if not meshes:
            raise RequiredSectionMissingError("No section matching './/3mf:resources/3mf:object/3mf:mesh'")
        mesh=meshes[0]
        verticess=mesh.findall('.//3mf:vertices',namespaces)
        if not verticess:
            raise RequiredSectionMissingError("No section matching './/3mf:vertices'")
        vertices=verticess[0]
        self.vertices=[np.array((float(vertex.attrib["x"]),float(vertex.attrib["y"]),float(vertex.attrib["z"]))).reshape(-1,1) for vertex in vertices]
        #print(self.vertices)
        triangless=mesh.findall('.//3mf:triangles',namespaces)
        if not triangless:
            raise RequiredSectionMissingError("No section matching './/3mf:triangles'")
        triangles=triangless[0]
        self.triangles=np.array([np.hstack((self.vertices[int(triangle.attrib["v1"])],
                                            self.vertices[int(triangle.attrib["v2"])],
                                            self.vertices[int(triangle.attrib["v3"])])) for triangle in triangles])
        self.tricolors=colors[:,np.array([int(triangle.attrib["p1"]) for triangle in triangles])]
        print(self.triangles.shape)
        print(self.tricolors.shape)
    def render_setup(self,M_cu:np.ndarray,T_c:np.ndarray):
        """
        Frame up a triangle mesh and prepare it for rendering.
        :param M_cu:
        :param T_c:
        :uses self.triangles: as tri_u, a 1D bundle of a 3x3 matrix representing 3 vectors for each triangle, so shape (M,3,3)
        :uses self.tricolors: as color for each triangle, shape (m
        :return: A tuple:


        Transformation *could* be T_u, where we have tri_uprime=tri_u+T_u, then run the camera transform.
        In this case, we would have tri_c=M_cu@(tri_u+T_u). A 1 unit displacement in x would go whichever direction
        universe x happens to be.
        OR
        we can have transformation at T_c, already in the camera frame. In this case, a 1 unit of z would move the spacecraft origin
        to the screen projection plane.
        tri_c=M_cu@(tri_u+T_u)
             =M_cu@tri_u+M_cu@T_u
             =M_cu@tri_u+T_c
        """
        # Do the transformation
        tri_c=T_c+M_cu@self.triangles
        # Cull the back-facing triangles.







