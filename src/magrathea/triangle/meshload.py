"""
Load a triangle mesh

Created: 8/28/25
"""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import numpy as np

from magrathea.triangle.mesh import Mesh


class RequiredSectionMissingError(LookupError):
    pass


def parse_html_color(color:str):
    return np.array((int(color[1:3],16),int(color[3:5],16),int(color[5:7],16)))/255

# begin literate_doc load3mf
def load3mf(infn:str|Path)-> Mesh:
    with ZipFile(infn, "r") as zip:
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
    colors=[]
    for color in colorgroup:
        colors.append(parse_html_color(color.attrib["color"]))
    colors=np.array(colors)
    meshes=root.findall('.//3mf:resources/3mf:object/3mf:mesh',namespaces)
    if not meshes:
        raise RequiredSectionMissingError("No section matching './/3mf:resources/3mf:object/3mf:mesh'")
    mesh=meshes[0]
    verticess=mesh.findall('.//3mf:vertices',namespaces)
    if not verticess:
        raise RequiredSectionMissingError("No section matching './/3mf:vertices'")
    vertices=verticess[0]
    vertices=[np.array((float(vertex.attrib["x"]),float(vertex.attrib["y"]),float(vertex.attrib["z"]))).reshape(-1,1) for vertex in vertices]
    #print(self.vertices)
    triangless=mesh.findall('.//3mf:triangles',namespaces)
    if not triangless:
        raise RequiredSectionMissingError("No section matching './/3mf:triangles'")
    triangles=triangless[0]
    tricolors=colors[np.array([int(triangle.attrib["p1"]) for triangle in triangles]),:]
    triangles=np.array([np.hstack((vertices[int(triangle.attrib["v1"])],
                                   vertices[int(triangle.attrib["v2"])],
                                   vertices[int(triangle.attrib["v3"])])) for triangle in triangles])
    print(triangles.shape)
    print(tricolors.shape)
    return Mesh(triangles=triangles, tricolors=tricolors)
# end literate_doc load3mf

