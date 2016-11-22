//* Incubator module for Waterscope *//
//* M. Delmans *//

//put the extruded edge on the bottom
//put the hole for cable adaptor

//* Size of a glass slide *//
slideW = 26; //25x 76 in reality 
slideL = 76;
slideH = 1;

//* Size of a cover glass *//
coverW = 23; // 25x25 in reality
coverH = 0.8;
paperH = 0.2;
frameW = 4; // Gene frame width


//* Size of a temperature sensor Dallas 18B20 *//
sensorL = 8;
sensorW = 5;
sensorH = 4;

//* field of view hole
viewing_hole_R = 10;
viewing_hole_H = 100;

//* base for screwing
sample_base_Y = 48;
sample_base_X = 35;
screw_R = 1; // radius of screw
screw_H = 30; //height of screw holes


//---------end of bottom part

//* Size of a resistor heater RS 159-758 *//
heaterW=20;
heaterL = 11.4;
heaterWW = 6; // Size of an overhang
heaterH = 11;

// this is the edge thickness
holderFlankW = 2;
$fn = 100;

// ---------- for top part --

//For top half
top_half_H = 10;

//* Stage module (bottom part) *//

// screws

   

// bottom part
module Stage(){
    
   module screws(){  
        translate([8.25, 19.05, -0.5*screw_H]) cylinder(screw_H, screw_R, screw_R);

        mirror([1,0,0]) {    
            translate([8.25, 19.05, -0.5*screw_H]) cylinder(screw_H, screw_R, screw_R);}
       
        mirror([0,1,0]) {
            translate([8.25, 19.05, -0.5*screw_H]) cylinder(screw_H, screw_R, screw_R);

            mirror([1,0,0]) {    
                translate([8.25, 19.05, -0.5*screw_H]) cylinder(screw_H, screw_R, screw_R);}
        }
    }
   

   
    
   module sensors(){
        // 3_wires  (6 wires)
        translate([0, 0, -0.25*sensorH]) cube([slideL, 0.2*sensorW, 0.5*sensorH], center = true);
        translate([0, 0.4*sensorW, -0.25*sensorH]) cube([slideL, 0.2*sensorW, 0.5*sensorH], center = true);
        translate([0, -0.4*sensorW, -0.25*sensorH]) cube([slideL, 0.2*sensorW, 0.5*sensorH], center = true);
        // 2 sensor
        translate([0.5*( coverW - 2*frameW + sensorL ), 0, 0]) cube([sensorL, sensorW, sensorH], center = true);
        
       mirror([0,1,0])
        translate([-0.5*( coverW - 2*frameW + sensorL ), 0, 0]) cube([sensorL, sensorW, sensorH], center = true);
   }    

   
   //now the stage
   difference(){
        // bottom piece 
        // same size as glass slide + flank + 
        union() {
        // top half 
            translate([0,0,0.5*top_half_H])cube([slideL, slideW + 2*holderFlankW, top_half_H], center = true);
        //cross base for screwing
            translate([0,0,0.5*top_half_H])cube([sample_base_X, sample_base_Y, top_half_H], center = true);
        }
       
        screws();
        mirror([0,0,1])sensors();

           
        //viewing hole
        translate([0, 0, -0.5*sensorH])cylinder(viewing_hole_H, viewing_hole_R, viewing_hole_R);


    }
}

//translate([0, 0, -20]) 
Stage();