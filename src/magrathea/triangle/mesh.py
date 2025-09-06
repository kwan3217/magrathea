"""
Describe purpose of this script here

Created: 8/29/25
"""
import numpy as np
from kwanmath.interp import linterp
from kwanmath.vector import vnormalize, vcross, vdot


class Mesh:
    def __init__(self,*,triangles:np.ndarray,tricolors:np.ndarray):
        """

        :param self.triangles: 1D bundle of triangle fibers, each of which itself is a 1D bundle of vertices,
                               IE a matrix with column vectors. Result has shape (M,3,3) where first index (size M)
                               is triangle index, second index (size 3) is 3D in Euclidean 3D space, and third index
                               (also size 3) is the vertex index of the triangles.
        :param self.tricolors: 1D bundle of colors, shape (M,3). Each row is a color of one triangle.
        """
        self.triangles=triangles
        self.tricolors=tricolors
    def shade_geometry(self,*,M_ub:np.ndarray,M_cu:np.ndarray,T_c:np.ndarray,
                       lhat_u:np.ndarray,diffuse:float=0.9,ambient:float=0.1,
                       w:int=None,h:int=None):
        """
        Perform the work of a geometry shader.

        * Transform body vertex coordinates to
        :param M_ub: Matrix which transforms to universe from body coordinates. This is a 3x3 matrix which leaves
                     the origin of the body at the origin of the universe. This is appropriate for the present use case.
                     It should usually be an SO(3) matrix.
        :param M_cu: Matrix which transforms to camera from universe coordinates. This includes field of view and aspect,
                     so while the basis vectors are orthogonal, they are generally *not* orthonormal, so M_cu is not
                     special orthogonal.
        :param T_c: Vector of translation of body center in camera space, effectively it's "stage position" relative to camera.
                    +x is right, -x is left, +y is down, -y is up, +z is in front of camera and visible, -z is behind camera
                    and invisible, with
        :param lhat_u: direction to light in universe frame
        :param diffuse: contribution of lambert reflection, default matches POV-Ray
        :param ambient: contribution of color independent of any lighting, default matches POV-Ray
        :uses self.triangles: as tris_b, a 1D bundle of a 3x3 matrix representing 3 vectors for each triangle, so shape (M,3,3)
        :uses self.tricolors: as color for each triangle, shape (M,3)
        :return: A tuple:
           * 2D vertices of triangles in normalized screen coordinates, with left edge at x=-0.5, right edge at x=+0.5,
                                                                             top edge at y=-0.5, bottom edge at y=+0.5.
             This is in the form of a bundle of size N of 2x3 matrices, therefore an (N,2,3) array, culled so only
             triangles in front of the camera are visible and sorted from far to near, so the painter's algorithm works.
           * Corresponding colors in the form of a bundle of RGB shaded vectors, shape (N,3) each component R (col 0),
             G (col 1) and B (col 2) between 0.0 and 1.0

        Translation *could* be T_u, where we have tri_uprime=tri_u+T_u, then run the camera transform.
        In this case, we would have tri_c=M_cu@(tri_u+T_u). A 1 unit displacement in x would go whichever direction
        universe x happens to be.
        OR
        we can have transformation at T_c, already in the camera frame. In this case, a 1 unit of z would move the spacecraft origin
        to the screen projection plane.
        tri_c=M_cu@(tri_u+T_u)
             =M_cu@tri_u+M_cu@T_u
             =M_cu@tri_u+T_c
        """
        # Transform triangles to universe space. This assumes body and universe frame origins coincide, correct for this use case
        tris_u=M_ub@self.triangles
        # Do lambert reflection in universe space
        edge_a_u=(tris_u[:,:,1]-tris_u[:,:,0]).T # Edge A vectors, shape 3,M
        edge_b_u=(tris_u[:,:,2]-tris_u[:,:,0]).T # Edge B vectors, shape 3,M
        nhat_u=vnormalize(vcross(edge_a_u,edge_b_u)) # unitized normal vectors, result is shape 3,M
        lambert=np.maximum(0,vdot(lhat_u,nhat_u)) # result is (M,) and triangles facing away from light get 0 Lambertian brightness.
        # Do the transformation to camera space
        tris_c=T_c+M_cu@tris_u
        # Cull the back-facing triangles and triangles behind the camera (z<0)
        edge_a_c=(tris_c[:,:,1]-tris_c[:,:,0]).T
        edge_b_c=(tris_c[:,:,2]-tris_c[:,:,0]).T
        normals_c=vcross(edge_a_c,edge_b_c)   # recalculate normals in camera space, result is shape 3,M.
                                              # don't need to normalize since we just check the sign of the dotp of this with direction.
        dotp=vdot(normals_c,tris_c[:,:,0].T)    # result is M, positive means normal is facing forward, away from camera, so seeing back side
                                              #              and therefore should be culled
        keep_mask=np.logical_and(dotp<0,tris_c[:,2,0]>0) # result is M, of bools, N of which are true
        tris_kept=tris_c[keep_mask]                # Result select out Nx3x3
        intrinsic_kept=self.tricolors[keep_mask] # Result selects out Nx3
        shade_kept=(diffuse*lambert[keep_mask]+ambient)
        trishades_kept=intrinsic_kept*shade_kept[:,None] # Add a dim so it's Nx1 and broadcasts with Nx3
        # Sort the culled triangles by (squared) distance to vertex 0. Do it negative so that further points are more negative and sort first
        negdist2=-vdot(tris_kept[:,:,0].T,tris_kept[:,:,0].T) # result is N,
        s=np.argsort(negdist2) # permutation list
        tris_sorted=tris_kept[s,:,:] # triangles sorted permutation list
        trishades_sorted=trishades_kept[s,:] # shading sorted by permutation list
        # Project the triangles by dividing by the z component
        tris_project=tris_sorted[:,0:2,:]/tris_sorted[:,2,None,:] # result is Nx2x3, a 2D vector for each vertex in N triangles
        if w is None:
            return tris_project,trishades_sorted
        x_screen = linterp(-0.5, 0, 0.5, w, tris_project[:, 0, :]).astype(np.int32)
        y_screen = linterp(-0.5, 0, 0.5, h, tris_project[:, 1, :]).astype(np.int32)
        tris_screen = np.stack((x_screen, y_screen), axis=1)
        return tris_screen,trishades_sorted


