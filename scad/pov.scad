// POV-Ray stuff
function vlength(v)=sqrt(v.x*v.x+v.y*v.y+v.z*v.z);
function vnormalize(v)=v/vlength(v);
module pov_cylinder(r1,r2,r) {
    /*
    :param r1: center of face 1
    :param r2: center of face 2
    :param r: radius of faces
    */
    zb=vnormalize(r2-r1); //axis of cylinder (on z axis in body frame)
    xb=vlength(cross(zb,[0,1,0]))==0.0?vnormalize(cross(zb,[1,0,0])):vnormalize(cross(zb,[0,1,0]));
    yb=vnormalize(cross(zb,xb));
    
    
    multmatrix([[xb.x,yb.x,zb.x,r1.x],
                [xb.y,yb.y,zb.y,r1.y],
                [xb.z,yb.z,zb.z,r1.z],
                [ 0.0, 0.0, 0.0, 1.0]])
    cylinder(h=vlength(r2-r1),r1=r,r2=r,center=false);
}

module pov_cone(r1,rr1,r2,rr2) {
    /*
    :param r1: center of face 1
    :param r2: center of face 2
    :param r: radius of faces
    */
    zb=vnormalize(r2-r1); //axis of cylinder (on z axis in body frame)
    xb=vlength(cross(zb,[0,1,0]))==0.0?vnormalize(cross(zb,[1,0,0])):vnormalize(cross(zb,[0,1,0]));
    yb=vnormalize(cross(zb,xb));
    
    
    multmatrix([[xb.x,yb.x,zb.x,r1.x],
                [xb.y,yb.y,zb.y,r1.y],
                [xb.z,yb.z,zb.z,r1.z],
                [ 0.0, 0.0, 0.0, 1.0]])
    cylinder(h=vlength(r2-r1),r1=rr1,r2=rr2,center=false);
}


