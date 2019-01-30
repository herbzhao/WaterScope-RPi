/*
  Blink

  Turns an LED on for one second, then off for one second, repeatedly.

  Most Arduinos have an on-board LED you can control. On the UNO, MEGA and ZERO
  it is attached to digital pin 13, on MKR1000 on pin 6. LED_BUILTIN is set to
  the correct LED pin independent of which board is used.
  If you want to know what pin the on-board LED is connected to on your Arduino
  model, check the Technical Specs of your board at:
  https://www.arduino.cc/en/Main/Products

  modified 8 May 2014
  by Scott Fitzgerald
  modified 2 Sep 2016
  by Arturo Guadalupi
  modified 8 Sep 2016
  by Colby Newman

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/Blink
*/

// constants won't change. Used here to set a pin number:
const int Pin1 =  2;// the number of the LED pin
const int Pin2 =  3;// the number of the LED pin
const int Pin3 =  4;// the number of the LED pin
const int Pin4 =  5;// the number of the LED pin

String x_motor_status = "stop";
String y_motor_status = "stop";
String z_motor_status = "stop";

// the setup function runs once when you press reset or power the board
void setup() {
  // start serial port
  Serial.begin(9600);
  Serial.setTimeout(50);


  // initialize digital pin LED_BUILTIN as an output.
  pinMode(Pin1, OUTPUT);
  pinMode(Pin2, OUTPUT);
  pinMode(Pin3, OUTPUT);
  pinMode(Pin4, OUTPUT);


  // initialise the speed of the motor
  increase_speed();
  turn("x+");
  turn("y+");
  turn("z+");  
}

// the loop function runs over and over again forever
void loop() {
  if (Serial.available()) 
  {
    String serial_input = Serial.readString();
    serial_condition(serial_input);  
  }
  
}


void send_2bit_code(int Pin1_val, int Pin2_val, int Pin3_val, int Pin4_val) {
  digitalWrite(Pin1, Pin1_val);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(Pin2, Pin2_val);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(Pin3, Pin3_val);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(Pin4, Pin4_val);   // turn the LED on (HIGH is the voltage level)
  delay(5);
  digitalWrite(Pin1, 0);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(Pin2, 0);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(Pin3, 0);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(Pin4, 0);   // turn the LED on (HIGH is the voltage level)
  delay(5);
  }

void turn(String condition){
  if (condition == "y+"){
    send_2bit_code(0,0,0,1);
    delay(5);
    }
  else if (condition == "y-"){
    send_2bit_code(0,1,0,0);
    delay(5);
    }
  else if (condition == "y++"){
    send_2bit_code(0,1,1,1);
    delay(5);
    }
  else if (condition == "y--"){
    send_2bit_code(1,0,0,0);
    delay(5);
    }
  else if (condition == "ystart"){
     for (int i=0; i <= 255; i++){
      send_2bit_code(0,1,1,1);
      delay(5);
     }
   }
    else if (condition == "ystop"){
     for (int i=0; i <= 255; i++){
      send_2bit_code(1,0,0,0);
      delay(5);
     }
   }

   
  else if (condition == "x+"){
    send_2bit_code(0,0,1,0);
    delay(5);
    }
  else if (condition == "x-"){
    send_2bit_code(0,0,1,1);
    delay(5);
    }
   else if (condition == "x++"){
    send_2bit_code(1,0,0,1);
    delay(5);
    }
  else if (condition == "x--"){
    send_2bit_code(1,0,1,0);
    delay(5);
    }
    
  else if (condition == "xstart"){
   for (int i=0; i <= 255; i++){
    send_2bit_code(1,0,0,1);
    delay(5);
   }
 }
  else if (condition == "xstop"){
   for (int i=0; i <= 255; i++){
    send_2bit_code(1,0,1,0);
    delay(5);
   }
 }


  else if (condition == "z+"){
    send_2bit_code(0,1,0,1);
    delay(5);
    }
   
  else if (condition == "z-"){
    send_2bit_code(0,1,1,0);
    delay(5);
    }  

   else if (condition == "z++"){
    send_2bit_code(1,0,1,1);
    delay(5);
    }
  else if (condition == "z--"){
    send_2bit_code(1,1,0,0);
    delay(5);
    }
  else if (condition == "zstart"){
   for (int i=0; i <= 255; i++){
    send_2bit_code(0,1,0,1);
    delay(5);
   }
 }
  else if (condition == "zstop"){
   for (int i=0; i <= 255; i++){
    send_2bit_code(1,1,0,0);
    delay(5);
   }
 }
}


void increase_speed(){
  turn("x++");
  turn("y++");
  turn("z++");
  turn("x++");
  turn("y++");
  turn("z++");
  turn("x++");
  turn("y++");
  turn("z++");
  turn("x++");
  turn("y++");
  turn("z++");
}



void serial_condition(String serial_input){
  //Serial.println(serial_input);
  // trim is needed as there is blank space and line break
  serial_input.trim();
  turn(serial_input);
  Serial.println(serial_input);
  // use zero speed to stop the motor? 
  // so that we can turn directly
}

