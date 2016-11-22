
//base is made with square - 4 square
base_square_L = 50.9;
base_substract_square_L = 15;
mid_part_H = 4; // equal to sensor_H as sensor_H
bottom_part_H = 2;
top_part_H = 6;

//holes for nuts
nut_R = 1.42;
nut_H = 50;
nut_distance_1 = 21.56;
nut_distance_2 = 13.08;
$fn = 36;

//glass slide
slide_W = 26;
slide_L = 76; //actual value is 25x75
slide_H = 2; //include glass slide + gene frame + cover slip
cover_W = 25; // cover slip size

//thermal sensor
//* Size of a temperature sensor Dallas 18B20 *//
sensor_L = 8; // this may be wrong, should be 5?
sensor_W = 5;
sensor_H = 4;

//sensor pins
sensor_pin_gap = 1.5; // horizontal difference between 3 pins
sensor_pin_ratio = 0.3; //wire height from the bottom of base plate
sensor_pin_W = 1; //actual value is 0.5?
sensor_pin_L = 100; //thorough wires


//viewing holes
viewing_hole_R = 12; //filter paper r = 6.5 
viewing_hole_H = 100;


//heating chamber  <-- this gives extra space for resistor not to touch plastic and blocking view
chamber_R_extra = 2;

//heating resistance
resistor_R = 1.5;
resistor_pin_gap = 5;
resistor_pin_W = 1;
resistor_pin_L = 100;
resistor_pin_H = 1;


module mirror_duplication(mirror_plane){//create a mirror object while keeping original object
    children();
    mirror(mirror_plane)children();
}

module quad_mirror(){  //mirror copy everything for four times. The children() object is at top right corner
    children();
    mirror([1,0,0])children();
    mirror([0,1,0]){    
        children();
        mirror([1,0,0])children();}
}

module base_plate(thickness){//base plate
    difference(){ 
    
    //base cube
    cube([base_square_L, base_square_L, thickness], center = true);

    //the substarcting squares -- make octagon
    quad_mirror(){
        translate([0.5*base_square_L,0.5*base_square_L,0])rotate(a=45,v=[0,0,1]){cube([base_substract_square_L, base_substract_square_L, thickness], center = true);}
    }
    
    
    //holes for nuts
    quad_mirror(){
        mirror_duplication([1,-1,0])translate([nut_distance_2,nut_distance_1, -0.5*nut_H])cylinder(nut_H, nut_R, nut_R);
    }
    
    {//viewing hole
    translate([0, 0, -1*thickness])
        cylinder(viewing_hole_H, viewing_hole_R, viewing_hole_R);
    }
    }
    

    }

difference(){ //middle part - base with thermal sensors + top part with heater
    mid_part_H = sensor_H;
    base_plate(mid_part_H);
    {//thermal sensors
        //sensors  
        //0.45*sensor_L because the circular shape
        mirror_duplication([1,0,0]){translate([viewing_hole_R+0.45*sensor_L, 0, -0.5*mid_part_H+0.5*sensor_H]) cube([sensor_L, sensor_W, sensor_H], center = true);}

        //wire 1,2,3
        translate([0, 0, (-0.5+sensor_pin_ratio)*mid_part_H+0.5*mid_part_H
        ])cube([sensor_pin_L, sensor_pin_W, mid_part_H], center = true);
        //wire 2
        translate([0, sensor_pin_gap, (-0.5+sensor_pin_ratio)*mid_part_H+0.5*mid_part_H])cube([sensor_pin_L, sensor_pin_W, mid_part_H], center = true);
        //wire 3
        mirror_duplication([0,1,0])translate([0, sensor_pin_gap, (-0.5+sensor_pin_ratio)*mid_part_H+0.5*mid_part_H])cube([sensor_pin_L, sensor_pin_W, mid_part_H], center = true);
        }

       
}


difference(){//top part
    //base plate
    translate([0, 0, 0.5*(mid_part_H+top_part_H)])base_plate(top_part_H);
    
    {//heating chamber
    chamber_R = 2*resistor_R + viewing_hole_R + chamber_R_extra;
    translate([0, 0, 0.5*(mid_part_H)]) cylinder(viewing_hole_H, chamber_R, chamber_R);}
    

    {//2 resistors
    mirror_duplication([0,1,0]){ // two resistors
    translate([0,-1*chamber_R+1.1*resistor_R,0.5*mid_part_H+0.5*top_part_H])
        union(){//heating resistor
            
        translate([-0.5*resistor_pin_gap,0,0])rotate(a=[0,90,0],v=[0,1,0])cylinder(resistor_pin_gap, resistor_R, resistor_R);
            
            
        mirror_duplication([1,0,0]){translate([-0.5*resistor_pin_gap,-0.5*resistor_pin_L,0])rotate(a=[0,0,90],v=[0,0,1])cube([resistor_pin_L, 2*resistor_pin_W, 2*resistor_pin_H], center = true);}
        }}
    }
    
}


            
    

difference(){ // bottom part
    
    //base_plate
    translate([0, 0, -0.5*(mid_part_H+bottom_part_H)])base_plate(bottom_part_H);

    {//glass slide
        translate([0, 0, -0.5*mid_part_H-bottom_part_H+0.5*slide_H])
        cube([slide_L,slide_W,slide_H],center = true);
    }
}






















