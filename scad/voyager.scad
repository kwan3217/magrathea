/* Notes:

* Blind idiot translation of VoyagerSimple.inc from POV-Ray
* Units are mostly in inches, reflecting the blueprint they are copied from
* -Z is high gain boresight

*/

use <pov.scad>

module stick(r1,r2,r) {
    /*
    :param r1: center of face 1
    :param r2: center of face 2
    :param r: radius of faces
    */
    $fn=3;
    pov_cylinder(r1,r2,r);
}


//Test Cylinders
 
/*
color([1,1,1]) pov_cylinder([0,0,0],[20,20,20],5);
color([1,0,0]) pov_cylinder([0,0,0],[100,0,0],1);
color([0,1,0]) pov_cylinder([0,0,0],[0,100,0],1);
color([0,0,1]) pov_cylinder([0,0,0],[0,0,100],1);
color([0,1,1]) pov_cylinder([-50,0,0],[-100,0,0],1);
color([1,0,1]) pov_cylinder([0,-50,0],[0,-100,0],1);
color([1,1,0]) pov_cylinder([0,0,-50],[0,0,-100],1);
pov_cylinder([0,0,0],[10,0,0],1);
pov_cylinder([10,0,0],[10,20,0],1);
pov_cylinder([10,20,0],[10,20,30],1);
pov_cylinder([0,0,0],[10,20,30],1);
*/

NSides=10;
FA=360/NSides;
BusR=37;
BusH=17;
$fn=16;

module decagon() {
  rotate([0,0,90])
  cylinder(h=1,r=1,$fn=NSides);
}

module box(v1,v2) {
    translate(v1)
    scale([v2.x-v1.x,v2.y-v1.y,v2.z-v1.z])
    cube(center=false);
}

module Louver() {
  translate([0.7,0,0])
  union() {
    LouverD=1;
    LouverInsetL=3;
    LouverInsetR=LouverInsetL;
    LouverInsetT=1;
    LouverInsetB=LouverInsetT;
    BladeN=8;
    // Note that sin and cos take angles in degrees
    LouverR= sin(FA/2)*BusR-LouverInsetR;
    LouverL=-sin(FA/2)*BusR+LouverInsetL;
    LouverW=LouverR-LouverL;
    LouverFrame=0.5;
    LouverX=cos(FA/2)*BusR;
    BladePitch=(LouverW-(2*LouverFrame))/BladeN;
    BladeOpen=30;
    color([1.0,1.0,1.0])
    box([LouverX        ,LouverL,-     LouverInsetT],
        [LouverX+LouverD,LouverR,-BusH+LouverInsetB]);
    for(I_Blade=[0:BladeN-1]) 
    translate([LouverX+LouverD,LouverL+LouverFrame+BladePitch*I_Blade,0])
    rotate([0,0,-BladeOpen])
    color([1.0,1.0,1.0])
    box([0  ,0         ,-LouverInsetT-LouverFrame],
        [0.1,BladePitch,-BusH+LouverInsetB+LouverFrame]);
  }
}


module Tubes(V,E,R) {
    /*
    :param V: list of vertices of shape [M,3] (so vectors are in rows)
    :param E: list of edges of shape [N,2] -- each edge is the zero-based index of start and end vertex of tube
    :param R: Tube radius
    */
    for(I=[0:len(E)-1]) stick(V[E[I][0]],V[E[I][1]],R);
}

module LaunchMount() {
  LaunchMountV=[
    [ 18, 25,0],[ 18,-25,0],
    [-18,-25,0],[-18, 25,0],
    [  0, 20,44.5],[ 20,  0,44.5],
    [  0,-20,44.5],[-20,  0,44.5],
  ];
  LaunchMountE=[
    [0,5],[1,5],
    [1,6],[2,6],
    [2,7],[3,7],
    [3,4],[0,4]
  ];
  color([0.5,0.5,0.5])
  Tubes(LaunchMountV,LaunchMountE,2);
}

RTGPivotZ=-24;
RTGPivotY=-60;

module RTGMount() {
  RTGMountV=[
    [ 21,-28,0], //0, bottom outboard +x
    [-21,-28,0], //1, bottom outboard -x
    [ 21,-28,-BusH], //2, top outboard +x
    [-21,-28,-BusH], //3, top outboard -x
    [0,-BusR,0],   //4,bottom inboard
    [ 11,RTGPivotY,RTGPivotZ],  //5,pivot +x
    [-11,RTGPivotY,RTGPivotZ],  //6,pivot +x
  ];
  RTGMountE=[
    [0,5],
    [2,5],
    [4,5],
    [1,6],
    [3,6],
    [4,6]
  ];
  color([1,1,1])
  Tubes(RTGMountV,RTGMountE,0.5);
}

module RTGTruss() {
  RTGTrussV=[
    [ 11,RTGPivotY,RTGPivotZ],  //0,pivot +x
    [-11,RTGPivotY,RTGPivotZ],  //1,pivot -x
    [  0, -84,-13],  //2 field joint x0
    [  8, -84,-18],  //3 field joint +x
    [ -8, -84,-18],  //4 field joint -x
    [  0,-104,-11],  //5 RTG x0
    [  3,-104,  0],  //6 RTG +x
    [ -3,-104,  0],  //7 RTG -x
  ];
  RTGTrussE=[
    [0,2],
    [0,3],
    [1,2],
    [1,4],
    [1,3],
    [2,3],
    [3,4],
    [4,2],
    [2,6],
    [2,7],
    [3,5],
    [3,6],
    [4,5],
    [4,7]
  ];
  color([1,1,1])
  Tubes(RTGTrussV,RTGTrussE,0.5);
}

module RTG() {
  color([0.5,0.5,0.5]) {
  pov_cylinder(
    [0,0,0],[0,-20,0],6
  )
  for(I=[0:3-1])
    rotate([0,120*I,0])
    box([-0.25,0,-8],[0.25,-20,8]);
  }
}

RTGStow=0.0;
MagBoomStow=0.0;

module RTGs() 
translate([0,RTGPivotY,RTGPivotZ])
rotate([-95*RTGStow,0,0])
translate([0,-RTGPivotY,-RTGPivotZ]) {
  RTGTruss();
  for(I=[0:3-1]) 
    translate([0,-103,-5])
    rotate([5,0,0])
    translate([0,-24*I,0])
    RTG();
}

module GoldRecord() {
  color([1.0,1.0,0.0])
  translate([-cos(FA/2)*BusR-0.01,1,-9.5])
  rotate([0,-90,0])
  cylinder(1,6,6,center=false);
}

module MainBus() {
  //main body of spacecraft, with no details. 10-bay structure, numbered
  //from bay 1 perpendicular to +X. Science boom attached to bays 3 and 4,
  //Gold Record to bay 6, RTGs to bays 8 and 9, star trackers to bay 10
  color([0.5,0.5,0.5,1])
  translate([0,1.12,0])
  difference() {
      translate([0,0,-BusH])
      scale([BusR,BusR,BusH])
      decagon();
      translate([0,0,-(BusH+1)])
      scale([BusR-8,BusR-8,BusH+2])
      decagon();
  }
}


module MagBoom() {
  MagBoomLength=13*39.97;
  MagBoomBays=60;
  MagBayLength=MagBoomLength/MagBoomBays;
  MagBoomR=5;
  WhipR=0.2;
  translate([0,-52,-28])
  rotate([40,0,0]) {
  color([1,1,1])
  pov_cylinder([0,0,0],[0,-16,0],MagBoomR);
  scale([1.0,1.0-MagBoomStow*0.97,1.0]) {
  for(I=[0:3-1]) color([1,0.75,0]) rotate([0,I*120+40,0]) stick(
      [0,-16,MagBoomR-WhipR],[0,-16-MagBoomLength,MagBoomR-WhipR],WhipR);
  for(I=[0:MagBoomBays-1]) translate([0,-(16+I*MagBayLength)])
      Tubes([
        [sin(0*120+40)*(MagBoomR-WhipR),0,cos(0*120+40)*(MagBoomR-WhipR)],
        [sin(1*120+40)*(MagBoomR-WhipR),0,cos(1*120+40)*(MagBoomR-WhipR)],
        [sin(2*120+40)*(MagBoomR-WhipR),0,cos(2*120+40)*(MagBoomR-WhipR)],
        [sin(0*120+40)*(MagBoomR-WhipR),-MagBayLength,cos(0*120+40)*(MagBoomR-WhipR)],
        [sin(1*120+40)*(MagBoomR-WhipR),-MagBayLength,cos(1*120+40)*(MagBoomR-WhipR)],
        [sin(2*120+40)*(MagBoomR-WhipR),-MagBayLength,cos(2*120+40)*(MagBoomR-WhipR)],
      ],[
        [0,4],
        [1,5],
        [2,3],
        [3,4],
        [4,5],
        [5,3]
      ],WhipR/2);
      }
  }
}

module shell(R,H,thick) {
  echo("len(R): ",len(R));
  RH=[
    for (i=[0:len(R)*2-1]) [
      R[i<len(R)?i:(2*len(R)-i-1)],
      H[i<len(H)?i:(2*len(H)-i-1)]+(i<len(R)?0:thick)
    ]
  ];
  echo("RH: ",RH);
  rotate_extrude() polygon(RH);
}

HGA_R=144.93/2; //numerator is diameter, exact value from blueprint
HGA_D=27; //depth measured from blueprint
HGA_c=HGA_D/(HGA_R*HGA_R);
HGA_t=1;
module HGADish() {
  Segments=2;
  HGA_rs=[for (r=[0:HGA_R/Segments:HGA_R]) r];
  echo("HGA_rs: ",HGA_rs);
  HGA_hs=[for (r=[0:HGA_R/Segments:HGA_R]) r*r*HGA_c];
  echo("HGA_hs: ",HGA_hs);
  CollarR=35;
  CollarD=HGA_c*CollarR*CollarR;
  translate([0,0,-36])
  scale([1,1,-1])
  color([1,1,1])
  shell(HGA_rs,HGA_hs,HGA_t);
  color([0.5,0.5,0.5])
  difference() {
      pov_cylinder([0,0,-33],[0,0,-36-CollarD],CollarR);
      pov_cylinder([0,0,-32],[0,0,-37-CollarD],CollarR-1);
  }
  /*translate([0,0,-36-HGA_D-HGA_t-1])
  cylinder(h=1,r=HGA_R);*/
}

module HGASupport() {
  color([0.5,0.5,0.5])
  Tubes([
    [-21,-28,-BusH],// 0, connecting point between bay 7 and 8
    [ 21,-28,-BusH],// 1, connecting point between bay 9 and 10
    [-28, 10,-BusH],// 2, connecting point between bay 5 and 6
    [-17,25,-BusH], // 3, between bay 4 and 5
    [ 28, 10,-BusH],// 4, connecting point between bay 1 and 2
    [ 17,25,-BusH], // 5, between bay 2 and 3
    [ 0,-34,-33], //6, dish connection between bay 8 and 9
    [-29,17,-33], //7, over bay 5,
    [ 29,17,-33], //7, over bay 2,
  ],[
    [0,6],
    [1,6],
    [2,7],
    [3,7],
    [4,8],
    [5,8]
  ],0.5);
}

module HGAFeed() {
  color([1,1,1]) {
    Tubes([
      [13*cos(0*120+90),13*sin(0*120+90),-87], //0
      [13*cos(1*120+90),13*sin(1*120+90),-87], //1
      [13*cos(2*120+90),13*sin(2*120+90),-87], //2
      [36*cos(0*120+30),36*sin(0*120+30),-36-HGA_c*36*36], //3
      [36*cos(1*120+30),36*sin(1*120+30),-36-HGA_c*36*36], //4
      [36*cos(2*120+30),36*sin(2*120+30),-36-HGA_c*36*36], //5
    ],[
      [3,0],
      [3,2],
      [4,0],
      [4,1],
      [5,1],
      [5,2]
    ],0.5);
    translate([0,0,-87.5])
    cylinder(h=7.5,r1=15,r2=0);
  }
  color([1,1,0])
  translate([0,0,-97])
  cylinder(h=9.5,r1=1.5,r2=4);
}

module PWA() {
  translate([0,-40,-20]) 
  rotate([-50,0,0])
  rotate([0,0,45]) {
    color([1,1,1])
    box([-3,-3,-3],[3,3,3]);
    color([1,0.5,0]) {
      pov_cylinder([0,0,0],[0,-10*39.37,0],0.2);
      pov_cylinder([0,0,0],[-10*39.37,0,0],0.2);
    }
  }
}

module ScienceTruss() {
  color([0.5,0.5,0.5])
  Tubes([
    [-17,25,-BusH], // 0, between bay 4 and 5
    [ 17,25,-BusH], // 1, between bay 2 and 3
    [  0,37,-BusH], // 2, between bay 3 and 4
    [ 8,45,-43], //3
    [-8,45,-43], //4
  ],[
    [0,3],
    [2,3],
    [1,4],
    [2,4],
    [1,3]
  ],0.5);
}
//Science boom measured 95.44" from deploy joint to center of azimuth joint,
//angle 8.56deg.
//angle 10.03deg stowed
module ScienceBoom() {
  translate([0,45,-43])
  rotate([-8.56,0,0])    //deployed position
  //rotate([90,0,0])  //stowed position
  color([0.5,0.5,0.5]) {
  Tubes([
    [ 8, 0, 0], //0
    [-8, 0, 0], //1
    [ 4, 5, 4], //2
    [ 4, 5,-4], //3
    [-4, 5,-4], //4
    [-4, 5, 4], //5
    [ 4,96, 4], //6
    [ 4,96,-4], //7
    [-4,96,-4], //8
    [-4,96, 4], //9
  ],[
    [0,2],
    [0,3],
    [1,4],
    [1,5],
    [2,3],[3,4],[4,5],[5,2],
    [2,6],[3,7],[4,8],[5,9]
  ],0.5);
  SciBoomNBays=7;
  SciBoomBayLen=12;
  for(IBay=[0:SciBoomNBays-1])
    translate([0,IBay*SciBoomBayLen+5,0])
    Tubes([
      [ 4, 0, 4], //0
      [ 4, 0,-4], //1
      [-4, 0,-4], //2
      [-4, 0, 4], //3
      [ 4,SciBoomBayLen, 4], //4
      [ 4,SciBoomBayLen,-4], //5
      [-4,SciBoomBayLen,-4], //6
      [-4,SciBoomBayLen, 4], //7
    ],[
      [0,1],[1,2],[2,3],[3,0],
      [0,7],[1,4],[2,5],[3,6]
    ],0.5);
    
    pov_cylinder([0,96,4.5],[0,96,-4.5],4.5);
    box([-4.5,89,-4.5],[4.5,96,4.5]);
    pov_cylinder([0,96,-8],[0,96,26],2);
  }
}

module FuelTank() {
  color([1.0,1.0,1.0,1])
  translate([0,0,-12.5])
  sphere(r=14);
}

module StarTracker() {
  translate([0,0,-BusH])
  rotate([0,0,180+35]) {
    color([0.5,0.5,0.5])
    box([0,0,0],[4.5,11,-5.5]);
    color([1.0,1.0,1.0])
    box([-0.5,11,3],[5.0,18,-8.5]);
  }
}

module StarTrackers() {
  translate([22.65,-15.65,0])
  StarTracker();
  translate([28.36, -7.92,0])
  StarTracker();
}

module VoyagerBody() {
  MainBus();
  rotate([0,0,-(1-1)*FA]) Louver();
  rotate([0,0,-(2-1)*FA]) Louver();
  rotate([0,0,-(5-1)*FA]) Louver();
  rotate([0,0,-(7-1)*FA]) Louver();
  GoldRecord();
  LaunchMount();
  RTGMount();
  RTGs();
  MagBoom();
  HGADish();
  HGASupport();
  HGAFeed();
  PWA();
  ScienceTruss();
  FuelTank();
  ScienceBoom();
  StarTrackers();
}

module ISSNA() {
  color([0.5,0.5,0.5])
  translate([-13,0,0]) {
    pov_cylinder([0,18,0],[0,-9,0],4.5);
    pov_cylinder([0,-9,0],[0,-18,0],3);
  }
}

module ISSWA() {
  color([0.5,0.5,0.5])
  translate([-13,0,-9]) {
    pov_cylinder([0,15,0],[0,5,0],1.5);
    pov_cylinder([0,5,0],[0,-4,0],3);
  }
}

module PPS() {
  color([0.5,0.5,0.5])
  translate([-13,0,9]) {
    pov_cylinder([0,-2,0],[0,-10,0],4);
    pov_cylinder([0,-10,0],[0,-15,0],3);
    difference() {
      pov_cylinder([0,18,0],[0,-10,0],4);
      pov_cylinder([0,19,0],[0,-11,0],3.5);
      rotate([0,-45,0])
      translate([0,5,0])
      rotate([70,0,0])
      box([-20,0,-20],[20,10,20]);
    }
//    clipped_by { plane {y,0 rotate x*70 translate y*5 rotate -y*45}}
  }
}

module IRIS() {
  translate([7,0,14]) {
    color([0.5,0.5,0.5]) {
      difference() {
        union() {
          pov_cylinder([0,11,0],[0,-8,0],11);
          pov_cone([0,-8,0],11,[0,-12,0],3.5);
        }
        pov_cylinder([0,12,0],[0,0.1,0],10.5);
        pov_cylinder([0,1,0],[0,0,0],10.4);
      }
      pov_cylinder([0,0,0],[0,14,0],1.5);
      pov_cone([0,14,0],3.5,[0,17,0],2.25);
    }
    color([1,1,0])
    pov_cylinder([0,1,0],[0,0,0],10.4);
  }
}

module UVIS() {
  color([0.5,0.5,0.5])
  box([17,10,4],[22,-10,10]);
}

module ScanPlatform() {
  rotate([0,0,90])
  rotate([90,0,0]) {
    ISSNA();
    ISSWA();
    PPS();
    IRIS();
    UVIS();
    color([0.5,0.5,0.5]) {
      box([-3,8,-16],[-8,-8,10]);
      box([4,6,-7],[16,-2,3]);
      pov_cylinder([-5,0,0],[22,0,0]);
    }
  }
  color([1,0,0])pov_cylinder([0,0,0],[100,0,0],1);
  color([0,1,0])pov_cylinder([0,0,0],[0,100,0],1);
  color([0,0,1])pov_cylinder([0,0,0],[0,0,500],1);
  color([0,1,1])pov_cylinder([0,0,0],[-100,0,0],1);
  color([1,0,1])pov_cylinder([0,0,0],[0,-100,0],1);
  color([1,1,0])pov_cylinder([0,0,0],[0,0,-100],1);
}

ScanPivot=[0,143,-29.5];

module Voyager() {
  scale([1/39.37,1/39.37,1/39.37]) {
    VoyagerBody();
    translate(ScanPivot)
    ScanPlatform();
  }
}

Voyager();