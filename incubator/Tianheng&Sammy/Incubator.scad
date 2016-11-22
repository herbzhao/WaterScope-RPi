//* Incubator module for Waterscope *//
//* M. Delmans *//


//* Size of a glass slide *//
slideW = 26;
slideL = 76;
slideH = 1;

//* Size of a cover glass *//
coverW = 23;
coverH = 0.8;
paperH = 0.2;
frameW = 4; // Gene frame width

//* Size of a temperature sensor Dallas 18B20 *//
sensorL = 8;
sensorW = 5;
sensorH = 4;

//* Size of an LED *//
ledH = 5;
ledR = 2.5;

//* Size of a resistor heater RS 159-758 *//
heaterW=20;
heaterL = 11.4;
heaterWW = 6; // Size of an overhang
heaterH = 11;

holderFlankW = 2;

$fn = 100;


//* Stage module (bottom part) *//
module Stage(){
    difference(){
        cube([slideL, slideW + 2*holderFlankW, sensorH], center = true);
        
        cube([coverW - 2*frameW, coverW - 2*frameW, sensorH], center = true);
        translate([ 0, 0, 0.5*(sensorH - coverH) ]) cube([coverW, coverW, coverH], center = true);
        
        translate([0.5*( coverW - 2*frameW + sensorL ), 0, 0]) cube([sensorL, sensorW, sensorH], center = true);
        translate([-0.5*( coverW - 2*frameW + sensorL ), 0, 0]) cube([sensorL, sensorW, sensorH], center = true);
        
        translate([0, 0, -0.25*sensorH]) cube([slideL, 0.2*sensorW, 0.5*sensorH], center = true);
        translate([0, 0.4*sensorW, -0.25*sensorH]) cube([slideL, 0.2*sensorW, 0.5*sensorH], center = true);
        translate([0, -0.4*sensorW, -0.25*sensorH]) cube([slideL, 0.2*sensorW, 0.5*sensorH], center = true);
    }
}

//* Holder Module (top part) *//
module Holder(){
        
    //* LED reflector shape *//
    module pyramid(h, baseW, r){
        intersection(){
            translate([0, 0, 0.5*h]) cube([baseW, baseW, h], center = true);
            cylinder(h, baseW, r);
        }
    }
    
    //* Cutout for resistor heater RS 159-758 *//
    module heater(){
        translate([-0.5*heaterL, 0.5*heaterW - heaterWW, 0])union(){
            cube([heaterL, heaterW, heaterH], center = true);
            translate([0.5*(heaterWW + heaterL), 0.5*(heaterWW - heaterW), 0])cube([heaterWW, heaterWW, heaterH], center = true);
            translate([-0.5*(heaterWW + heaterL), -0.5*(heaterWW - heaterW), 0])cube([heaterWW, heaterWW, heaterH], center = true);
        }
    }
    
    difference(){
        cube([slideL, slideW+2*holderFlankW, slideH + heaterH], center = true);
        translate([0, 0, -0.5*heaterH]) cube([slideL, slideW, slideH ], center = true);
        translate([0, 0, 0.5*(slideH - heaterH) ]) pyramid(h = heaterH - ledH, baseW = slideW - 2*heaterWW, r = ledR);
        translate([0, 0, -0.5*(heaterH+slideH - paperH) + slideH])cube([coverW, coverW, paperH], center = true);
        translate([0, 0, 0.5*(heaterH + slideH) - ledH]) cylinder(ledH, ledR, ledR);
        translate([-0.5*slideW + frameW, -0.5*slideW + heaterWW, 0.5*slideH]) heater();
        rotate([0, 0, 180])translate([-0.5*slideW + frameW, -0.5*slideW + heaterWW, 0.5*slideH]) heater();
        translate([-0.5*slideW + frameW - 0.5*heaterL, 0, -0.5*slideH])cube([3, slideW + 2*holderFlankW, heaterH], center = true);
        translate([0.5*slideW - frameW + 0.5*heaterL, 0, -0.5*slideH])cube([3, slideW + 2*holderFlankW, heaterH], center = true);
    }
}

translate([0, 0, 20]) Holder();
translate([0, 0, -20]) Stage();