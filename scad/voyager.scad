/* Notes:

Bus is not centered on rotation axis (1.12 inch offset towards +Y)
CG of spacecraft is not on rotation axis (

*/


module decagon() {
  rotate([0,0,90])
  cylinder(h=1,r=1,$fn=10);
}

BusR=38;
BusH=17;
    

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

module fueltank() {
  color([1.0,1.0,1.0,1])
  translate([0,0,-12.5])
  sphere(r=14);
}

MainBus();
fueltank();