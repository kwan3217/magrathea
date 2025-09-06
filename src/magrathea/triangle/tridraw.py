"""
Describe purpose of this script here

Created: 8/28/25
"""
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

Combiner=Callable[[np.ndarray|float,np.ndarray|float],np.ndarray|float]
replace=lambda a,b:b
default_combiner=replace


def is_top_left(ax: int, ay: int, bx: int, by: int) -> bool:
    # Top edge: horizontal (ay == by), leftward (ax > bx)
    # Left edge: downward (ay < by)
    return (ay == by and ax > bx) or (ay < by)


def tri_raster_scan(frame_buffer: np.ndarray, color: np.ndarray, xa: int, ya: int, xb: int, yb: int, xc: int, yc: int) -> None:

    # Check framebuffer and color shapes
    assert frame_buffer.ndim == 3 and frame_buffer.shape[2] == 3, "frame_buffer must be (height, width, 3)"
    assert color.shape == (3,), "color must be shape (3,)"

    height, width, _ = frame_buffer.shape

    # Compute twice the signed area to check for degeneracy
    twice_area = (xb - xa) * (yc - ya) - (xc - xa) * (yb - ya)
    if twice_area <= 0:
        return  # Degenerate or incorrectly oriented (assuming CCW)

    # Compute bounding box
    min_x = min(xa, xb, xc)
    max_x = max(xa, xb, xc)
    min_y = min(ya, yb, yc)
    max_y = max(ya, yb, yc)

    # Clamp to framebuffer bounds
    min_x = max(0, min_x)
    max_x = min(width - 1, max_x)
    min_y = max(0, min_y)
    max_y = min(height - 1, max_y)

    # Early exit if no overlap
    if min_x > max_x or min_y > max_y:
        return

    # Rasterize with top-left rule
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            # Orient2D tests for each edge
            d0 = (xb - xa) * (y - ya) - (x - xa) * (yb - ya)
            d1 = (xc - xb) * (y - yb) - (x - xb) * (yc - yb)
            d2 = (xa - xc) * (y - yc) - (x - xc) * (ya - yc)

            # Apply top-left rule biases
            bias0 = 0 if is_top_left(xa, ya, xb, yb) else -1
            bias1 = 0 if is_top_left(xb, yb, xc, yc) else -1
            bias2 = 0 if is_top_left(xc, yc, xa, ya) else -1

            if (d0 + bias0 >= 0) and (d1 + bias1 >= 0) and (d2 + bias2 >= 0):
                frame_buffer[y, x, :] = color


def tri_raster_bounds(frame_buffer: np.ndarray, color: np.ndarray, xa: int, ya: int, xb: int, yb: int, xc: int,
               yc: int) -> None:
    # Check framebuffer and color shapes
    assert frame_buffer.ndim == 3 and frame_buffer.shape[2] == 3, "frame_buffer must be (height, width, 3)"
    assert color.shape == (3,), "color must be shape (3,)"

    height, width, _ = frame_buffer.shape

    # Compute twice the signed area to check for degeneracy
    twice_area = (xb - xa) * (yc - ya) - (xc - xa) * (yb - ya)
    if twice_area <= 0:
        return  # Degenerate or incorrectly oriented (assuming CCW)

    # Compute bounding box
    min_y = min(ya, yb, yc)
    max_y = max(ya, yb, yc)

    # Clamp to framebuffer bounds
    min_y = max(0, min_y)
    max_y = min(height - 1, max_y)

    # Early exit if no overlap
    if min_y > max_y:
        return

    # Sort vertices by y to simplify scanline processing
    points = [(xa, ya), (xb, yb), (xc, yc)]
    points.sort(key=lambda p: (p[1], p[0]))  # Sort by y, then x for equal y
    (x0, y0), (x1, y1), (x2, y2) = points

    # Precompute edge slopes (dx/dy) for active edges
    # Edge 0-1 and 0-2 for y in [y0, y1), then 1-2 and 0-2 for y in [y1, y2]
    if y0 == y1:
        # Flat top: single segment from y0 to y2
        if y1 == y2:
            return  # All points at same y, degenerate
        inv_slope_a = (x2 - x0) / (y2 - y0) if y2 != y0 else 0
        inv_slope_b = (x2 - x1) / (y2 - y1) if y2 != y1 else 0
        for y in range(min_y, max_y + 1):
            # Compute x intersections
            xa = x0 + int((y - y0) * inv_slope_a + 0.5)  # Round to nearest
            xb = x1 + int((y - y1) * inv_slope_b + 0.5)
            # Apply top-left rule
            bias_a = 0 if is_top_left(x0, y0, x2, y2) else -1
            bias_b = 0 if is_top_left(x1, y1, x2, y2) else -1
            min_x = max(0, min(xa, xb) + bias_a)
            max_x = min(width - 1, max(xa, xb) + bias_b)
            if min_x <= max_x:
                frame_buffer[y, min_x:max_x, :] = color
    elif y1 == y2:
        # Flat bottom: single segment from y0 to y1
        inv_slope_a = (x1 - x0) / (y1 - y0) if y1 != y0 else 0
        inv_slope_b = (x2 - x0) / (y2 - y0) if y2 != y0 else 0
        for y in range(min_y, max_y + 1):
            xa = x0 + int((y - y0) * inv_slope_a + 0.5)
            xb = x0 + int((y - y0) * inv_slope_b + 0.5)
            bias_a = 0 if is_top_left(x0, y0, x1, y1) else -1
            bias_b = 0 if is_top_left(x0, y0, x2, y2) else -1
            min_x = max(0, min(xa, xb) + bias_a)
            max_x = min(width - 1, max(xa, xb) + bias_b)
            if min_x <= max_x:
                frame_buffer[y, min_x:max_x, :] = color
    else:
        # General case: split at y1
        inv_slope_a = (x1 - x0) / (y1 - y0) if y1 != y0 else 0
        inv_slope_b = (x2 - x0) / (y2 - y0) if y2 != y0 else 0
        inv_slope_c = (x2 - x1) / (y2 - y1) if y2 != y1 else 0
        # First segment: y0 to y1
        for y in range(min_y, min(max_y + 1, y1)):
            xa = x0 + int((y - y0) * inv_slope_a + 0.5)
            xb = x0 + int((y - y0) * inv_slope_b + 0.5)
            bias_a = 0 if is_top_left(x0, y0, x1, y1) else -1
            bias_b = 0 if is_top_left(x0, y0, x2, y2) else -1
            min_x = max(0, min(xa, xb) + bias_a)
            max_x = min(width - 1, max(xa, xb) + bias_b)
            if min_x <= max_x:
                frame_buffer[y, min_x:max_x, :] = color
        # Second segment: y1 to y2
        for y in range(max(y1, min_y), max_y + 1):
            xa = x1 + int((y - y1) * inv_slope_c + 0.5)
            xb = x0 + int((y - y0) * inv_slope_b + 0.5)
            bias_a = 0 if is_top_left(x1, y1, x2, y2) else -1
            bias_b = 0 if is_top_left(x0, y0, x2, y2) else -1
            min_x = max(0, min(xa, xb) + bias_a)
            max_x = min(width - 1, max(xa, xb) + bias_b)
            if min_x <= max_x:
                frame_buffer[y, min_x:max_x, :] = color


@dataclass
class Point2D:
    x:int
    y:int
    # Some algorithms (I'm looking at you, ssloy) use p[0] for p.x
    def __getitem__(self,key:int)->int:
        return self.x if key==0 else self.y
    def __add__(self,V:'Point2D'):
        if not isinstance(V,Point2D):
            return NotImplemented
        return Point2D(self.x+V.x,self.y+V.y)
    def __sub__(self,V:'Point2D'):
        if not isinstance(V,Point2D):
            return NotImplemented
        return Point2D(self.x-V.x,self.y-V.y)
    def __mul__(self,f:float):
        if not isinstance(f,float):
            return NotImplemented
        return Point2D(self.x*f,self.y*f)
    def __rmul__(self,f:float):
        if not isinstance(f,float):
            return NotImplemented
        return Point2D(self.x*f,self.y*f)



@dataclass
class Point3D:
    x:int
    y:int
    z:int
    def __getitem__(self,key:int)->int:
        return self.x if key==0 else (self.y if key==1 else self.z)
    def __add__(self,V:'Point3D'):
        if not isinstance(V,Point3D):
            return NotImplemented
        return Point3D(self.x+V.x,self.y+V.y,self.z+V.z)
    def __sub__(self,V:'Point3D'):
        if not isinstance(V,Point3D):
            return NotImplemented
        return Point3D(self.x-V.x,self.y-V.y,self.z-V.z)
    def __mul__(self,f:float):
        if not isinstance(f,float):
            return NotImplemented
        return Point3D(self.x*f,self.y*f,self.z*f)
    def __rmul__(self,f:float):
        if not isinstance(f,float):
            return NotImplemented
        return Point3D(self.x*f,self.y*f,self.z*f)
    # Override ^ for cross product. I don't like it either, but again ssloy did it in his code
    def __xor__(self,v:'Point3D')->'Point3D':
        if not isinstance(v,Point3D):
            return NotImplemented
        return Point3D(self.y*v.z-self.z*v.y, self.z*v.x-self.x*v.z, self.x*v.y-self.y*v.x)


def orient2d(a:Point2D, b:Point2D, c:Point2D)->int:
    return (b.x-a.x)*(c.y-a.y) - (b.y-a.y)*(c.x-a.x)


def drawTri(frame_buffer: np.ndarray, color: np.ndarray, xa: int, ya: int, xb: int, yb: int, xc: int, yc: int):
    # Compute triangle bounding box
    v0=Point2D(x=xa,y=ya)
    v1=Point2D(x=xb,y=yb)
    v2=Point2D(x=xc,y=yc)
    screenHeight,screenWidth,nChannels=frame_buffer.shape
    minX:int = np.min((v0.x, v1.x, v2.x))
    minY:int = np.min((v0.y, v1.y, v2.y))
    maxX:int = np.max((v0.x, v1.x, v2.x))
    maxY:int = np.max((v0.y, v1.y, v2.y))

    # Clip against screen bounds
    minX = max(minX, 0);
    minY = max(minY, 0);
    maxX = min(maxX, screenWidth - 1);
    maxY = min(maxY, screenHeight - 1);

    # Rasterize
    p=Point2D(None,None);
    for p.y in range(minY,maxY+1):
        for p.x in range(minX,maxX+1):
            # Determine barycentric coordinates
            w0:int = orient2d(v1, v2, p);
            w1:int = orient2d(v2, v0, p);
            w2:int = orient2d(v0, v1, p);

            # If p is on or inside all edges, render pixel.
            if (w0 >= 0 and w1 >= 0 and w2 >= 0):
                # renderPixel uses barycentric coords to do texture mapping etc. We just paint.
                #renderPixel(p, w0, w1, w2);
                #if not np.all(np.isnan(frame_buffer[p.y,p.x,:])):
                #    assert np.all(np.isnan(frame_buffer[p.y,p.x,:])),"Repainting the frame buffer"
                frame_buffer[p.y,p.x,:]+=color



def drawTriangle(frame_buffer: np.ndarray, color: np.ndarray, A:Point2D, B:Point2D, C:Point2D,combine:Callable[[np.ndarray,np.ndarray],np.ndarray]=replace):
    """
    Draw a triangle, using code from https://jtsorlinis.github.io/rendering-tutorial/

    """
    def edgeFunction(a: Point2D, b: Point2D, c: Point2D)->int:
        """
        Returns positive for "right side" of edge, negative for "left side".


        :param a:
        :param b:
        :param c:
        :return: double the signed area but that's fine
        """
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    # Calculate the edge function for the whole triangle (ABC)
    ABC = edgeFunction(A, B, C)
    # Our nifty trick: Don't bother drawing the triangle if it's back facing
    if (ABC < 0):
        Btemp=C
        C=B
        B=Btemp
        ABC=-ABC

    # Initialise our point
    P = Point2D(0, 0)

    # Get the bounding box of the triangle
    minX = np.maximum(np.min((A.x, B.x, C.x)),0)
    minY = np.maximum(np.min((A.y, B.y, C.y)),0)
    maxX = np.minimum(np.max((A.x, B.x, C.x)),frame_buffer.shape[1])
    maxY = np.minimum(np.max((A.y, B.y, C.y)),frame_buffer.shape[0])

    # Loop through all the pixels of the bounding box
    for i_y in range(minY,maxY):
        xrow_min=None
        xrow_max=None
        for i_x in range(minX,maxX):
            P.x=i_x
            P.y=i_y
            # Calculate our edge functions
            ABP = edgeFunction(A, B, P)
            BCP = edgeFunction(B, C, P)
            CAP = edgeFunction(C, A, P)


            # This is barycentric stuff we don't care about
            if False:
                # Normalise the edge functions by dividing by the total area to get the barycentric coordinates
                weightA = BCP / ABC
                weightB = CAP / ABC
                weightC = ABP / ABC

            # If all the edge functions are positive, the point is inside the triangle
            if (ABP >= 0 and BCP >= 0 and CAP >= 0):
                if xrow_min is None:
                    xrow_min=i_x
                # More interpolation stuff we don't care about. We would need to get colo(u)r[ABC] in as well.
                # Interpolate the colours at point P
                if False:
                    r = colourA.r * weightA + colourB.r * weightB + colourC.r * weightC
                    g = colourA.g * weightA + colourB.g * weightB + colourC.g * weightC
                    b = colourA.b * weightA + colourB.b * weightB + colourC.b * weightC
                    colourP = Colour(r, g, b)

                # Draw the pixel
            elif xrow_min is not None:
                xrow_max=i_x
                break
        if xrow_min is not None:
            if xrow_max is None:
                xrow_max=maxX
            frame_buffer[i_y, xrow_min:xrow_max,...]=combine(frame_buffer[i_y,xrow_min:xrow_max,...],color)


def ssloylinesweep_triangle(t0:Point2D,t1:Point2D,t2:Point2D,image:np.ndarray,color:np.ndarray,*,combine:Combiner=default_combiner):
    """
    From https://github.com/ssloy/tinyrenderer/wiki/Lesson-2:-Triangle-rasterization-and-back-face-culling

    :param t0:
    :param t1:
    :param t2:
    :param image:
    :param color:
    :param combine:
    :return:
    """
    if (t0.y==t1.y and t0.y==t2.y): 
        return  # I dont care about degenerate triangles 
    # sort the vertices, t0, t1, t2 lower−to−upper (bubblesort yay!)
    if (t0.y>t1.y): t1,t0=t0, t1
    if (t0.y>t2.y): t2,t0=t0, t2
    if (t1.y>t2.y): t2,t1=t1, t2
    total_height = t2.y-t0.y
    for i in range(total_height):
        second_half = (i>t1.y-t0.y) or (t1.y==t0.y)
        segment_height = t2.y-t1.y if second_half else t1.y-t0.y
        alpha = i/total_height
        beta  = (i-(t1.y-t0.y if second_half else 0))/segment_height # be careful: with above conditions no division by zero here
        A =               t0 + (t2-t0)*alpha
        B = t1 + (t2-t1)*beta if second_half else t0 + (t1-t0)*beta
        if (A.x>B.x): B,A=A,B
        for j in range(int(A.x),int(B.x+1)):
            image[t0.y+i,j,...]=combine(image[t0.y+i,j,...],color) # attention, due to int casts t0.y+i != A.y


def ssloybary_triangle(pts:list[Point2D],image:np.ndarray,color:np.ndarray,*,combine:Combiner=default_combiner):
    """
    From https://github.com/ssloy/tinyrenderer/wiki/Lesson-2:-Triangle-rasterization-and-back-face-culling
    :param pts:
    :param image:
    :param color:
    :return:
    """
    def barycentric(pts:list[Point2D], P:Point2D)->Point3D:
        u = Point3D(pts[2][0]-pts[0][0], pts[1][0]-pts[0][0], pts[0][0]-P[0])^Point3D(pts[2][1]-pts[0][1], pts[1][1]-pts[0][1], pts[0][1]-P[1])
        # `pts` and `P` has integer value as coordinates
        # so `abs(u[2])` < 1 means `u[2]` is 0, that means
        # triangle is degenerate, in this case return something with negative coordinates */
        if (np.abs(u.z)<1):
            return Point3D(-1,1,1)
        return Point3D(1.0-(u.x+u.y)/u.z, u.y/u.z, u.x/u.z)
    bboxmin=Point2D(image.shape[1]-1,  image.shape[0]-1)
    bboxmax=Point2D(0, 0)
    clamp=Point2D(image.shape[1]-1, image.shape[0]-1)
    for  i in range(0,3):
        bboxmin.x = np.max((0, np.min((bboxmin.x, pts[i].x))))
        bboxmin.y = np.max((0, np.min((bboxmin.y, pts[i].y))))

        bboxmax.x = np.min((clamp.x, np.max((bboxmax.x, pts[i].x))))
        bboxmax.y = np.min((clamp.y, np.max((bboxmax.y, pts[i].y))))
    P=Point2D(None,None)
    for P.x in range(bboxmin.x,bboxmax.x+1):
        for P.y in range(bboxmin.y, bboxmax.y+1):
            bc_screen  = barycentric(pts, P);
            if (bc_screen.x<0 or bc_screen.y<0 or bc_screen.z<0):
                continue
            image[P.y,P.x,...]=combine(image[P.y,P.x,...],color)


def bary2_triangle(pts:np.ndarray,image:np.ndarray,color:np.ndarray,*,combine:Combiner=default_combiner):
    """
    From https://github.com/ssloy/tinyrenderer/wiki/Lesson-2:-Triangle-rasterization-and-back-face-culling
    Adapted to
    :param pts: 2x3, 2D, 3 corners
    :param image:frame buffer 
    :param color:color to paint triangle
    """
    def barycentric(pts_array:np.ndarray, P:Point2D)->Point3D:
        pts_list=[Point2D(pts_array[0][i],pts_array[1][i]) for i in range(3)]
        u = Point3D(pts_list[2][0]-pts_list[0][0],
                    pts_list[1][0]-pts_list[0][0],
                    pts_list[0][0]-P[0]
                    )^Point3D(pts_list[2][1]-pts_list[0][1],
                              pts_list[1][1]-pts_list[0][1],
                              pts_list[0][1]-P[1])
        # `pts` and `P` has integer value as coordinates
        # so `abs(u[2])` < 1 means `u[2]` is 0, that means
        # triangle is degenerate, in this case return something with negative coordinates */
        if (np.abs(u.z)<1):
            return Point3D(-1,1,1)
        return Point3D(1.0-(u.x+u.y)/u.z, u.y/u.z, u.x/u.z)
    bboxmin=Point2D(image.shape[1]-1,  image.shape[0]-1)
    bboxmax=Point2D(0, 0)
    clamp=Point2D(image.shape[1]-1, image.shape[0]-1)
    for  i in range(0,3):
        bboxmin.x = np.max((0, np.min((bboxmin.x, pts[i].x))))
        bboxmin.y = np.max((0, np.min((bboxmin.y, pts[i].y))))

        bboxmax.x = np.min((clamp.x, np.max((bboxmax.x, pts[i].x))))
        bboxmax.y = np.min((clamp.y, np.max((bboxmax.y, pts[i].y))))
    Px=np.arange(bboxmin.x,bboxmax.x+1,dtype=np.int32).reshape(1,-1)
    Py=np.arange(bboxmin.y,bboxmax.y+1,dtype=np.int32).reshape(-1,1)
    P=Point2D(None,None)
    for P.x in range(bboxmin.x,bboxmax.x+1):
        for P.y in range(bboxmin.y, bboxmax.y+1):
            bc_screen  = barycentric(pts, P);
            if (bc_screen.x<0 or bc_screen.y<0 or bc_screen.z<0):
                continue
            image[P.y,P.x,...]=combine(image[P.y,P.x,...],color)



def grok_tri(frame_buffer:np.ndarray,pts:np.ndarray,color:np.ndarray,combine:Combiner=default_combiner):
    """

    :param frame_buffer: Frame buffer, shape (H,W,3)
    :param pts:          Triangle to draw, shape (2,3)
    :param color:        Color, shape (3,)
    :return: None, but draw the triangle in the frame buffer
    """
    def inside_triangle(pts:np.ndarray, Px:int, Py:int)->bool:
        #return Point3D(self.y * v.z - self.z * v.y, self.z * v.x - self.x * v.z, self.x * v.y - self.y * v.x)
        ax=pts[0,2]-pts[0,0]
        ay=pts[0,1]-pts[0,0]
        az=pts[0,0]-Px
        bx=pts[1,2]-pts[1,0]
        by=pts[1,1]-pts[1,0]
        bz=pts[1,0]-Py
        cx=ay*bz-az*by
        cy=az*bx-ax*bz
        cz=ax*by-ay*bx
        cross0 = (pts[0,1] - pts[0,0]) * (Py - pts[1,0]) - (pts[1,1] - pts[1,0]) * (Px - pts[0,0])
        cross1 = (pts[0,2] - pts[0,1]) * (Py - pts[1,1]) - (pts[1,2] - pts[1,1]) * (Px - pts[0,1])
        cross2 = (pts[0,0] - pts[0,2]) * (Py - pts[1,2]) - (pts[1,0] - pts[1,2]) * (Px - pts[0,2])
        return (cx >= 0 and cy >= 0 and cz >= 0)
    rows_fb:int=frame_buffer.shape[0]
    cols_fb:int=frame_buffer.shape[1]
    bboxmin_x:int = cols_fb - 1
    bboxmin_y:int = rows_fb - 1
    bboxmax_x:int = 0
    bboxmax_y:int = 0

    clamp_x:int = cols_fb - 1
    clamp_y:int = rows_fb - 1
    for i in range(3):
        bboxmin_x = 0 if (0 > pts[0,i]) else (bboxmin_x if bboxmin_x < pts[0,i] else pts[0,i])
        bboxmin_y = 0 if (0 > pts[1,i]) else (bboxmin_y if bboxmin_y < pts[1,i] else pts[1,i])
        bboxmax_x = clamp_x if (clamp_x < pts[0,i]) else (bboxmax_x if bboxmax_x > pts[0,i] else pts[0,i])
        bboxmax_y = clamp_y if (clamp_y < pts[1,i]) else (bboxmax_y if bboxmax_y > pts[1,i] else pts[1,i])
    for Px in range(bboxmin_x,bboxmax_x+1):
        for Py in range(bboxmin_y,bboxmax_y+1):
            if not inside_triangle(pts, Px, Py):
                continue
            frame_buffer[Py,Px,:] = combine(frame_buffer[Py,Px,:],color)


import numpy as np


def tri_raster_npmask(frame_buffer: np.ndarray, triangle: np.ndarray, tricolor: np.ndarray):
    """
    Rasterize a triangle into a frame buffer using edge functions.
    :param frame_buffer: shape (H, W, 3) for RGB color
    :param triangle: shape (2, 3), each column is a 2D vertex [x, y]
    :param tricolor: shape (3,), flat RGB color
    """
    H, W, _ = frame_buffer.shape

    # Compute bounding box
    x_min = np.floor(np.min(triangle[0])).astype(int)
    x_max = np.ceil(np.max(triangle[0])).astype(int)
    y_min = np.floor(np.min(triangle[1])).astype(int)
    y_max = np.ceil(np.max(triangle[1])).astype(int)

    # Clamp to frame buffer bounds
    x_min = max(0, x_min)
    x_max = min(W - 1, x_max)
    y_min = max(0, y_min)
    y_max = min(H - 1, y_max)

    # Skip if bounding box is empty
    if x_max < x_min or y_max < y_min:
        return

    # Create 2D grid of pixel centers
    i_x = np.arange(x_min, x_max + 1).reshape(1, -1)
    i_y = np.arange(y_min, y_max + 1).reshape(-1, 1)

    # Edge functions for all three edges
    def edge_function(va, vb, x, y):
        return (x - va[0]) * (vb[1] - va[1]) - (y - va[1]) * (vb[0] - va[0])

    # Compute edge functions over grid
    in_edge0 = edge_function(triangle[:, 1], triangle[:, 2], i_x, i_y)  # V1 -> V2
    in_edge1 = edge_function(triangle[:, 2], triangle[:, 0], i_x, i_y)  # V2 -> V0
    in_edge2 = edge_function(triangle[:, 0], triangle[:, 1], i_x, i_y)  # V0 -> V1

    # Pixels inside triangle (all edge functions >= 0)
    in_triangle = (in_edge0 >= 0) & (in_edge1 >= 0) & (in_edge2 >= 0)

    # Assign color to frame buffer
    frame_buffer[y_min:y_max + 1, x_min:x_max + 1, :][in_triangle, :] = tricolor


#tri_raster=drawTri
#tri_raster=lambda frame_buffer, color, xa, ya, xb, yb, xc, yc,combine:drawTriangle(frame_buffer,color,Point2D(xa,ya),Point2D(xb,yb),Point2D(xc,yc),combine=combine)
#tri_raster=lambda frame_buffer, color, xa, ya, xb, yb, xc, yc,combine=default_combiner:ssloybary_triangle([Point2D(xa,ya),Point2D(xb,yb),Point2D(xc,yc)],frame_buffer,color,combine=combine)
#tri_raster=lambda frame_buffer, color, xa, ya, xb, yb, xc, yc,combine:ssloylinesweep_triangle(Point2D(xa,ya),Point2D(xb,yb),Point2D(xc,yc),frame_buffer,color,combine=combine)
tri_raster_grok=lambda frame_buffer,color,xa,ya,xb,yb,xc,yc,combine=default_combiner:grok_tri(frame_buffer,np.array([[xa,xb,xc],[ya,yb,yc]]),color,combine=combine)
tri_raster=lambda frame_buffer, color, xa, ya, xb, yb, xc, yc,combine=default_combiner:tri_raster_npmask(frame_buffer,np.array([[xa,xb,xc],[ya,yb,yc]]),color)
