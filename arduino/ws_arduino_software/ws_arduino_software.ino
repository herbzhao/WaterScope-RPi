#include <PID_v1.h>
double PID_setpoint, PID_input, PID_output;
//Define the aggressive and conservative Tuning Parameters
// https://robotics.stackexchange.com/questions/9786/how-do-the-pid-parameters-kp-ki-and-kd-affect-the-heading-of-a-differential
double Kp=4, Ki=5, Kd=1;
//Specify the links and initial tuning parameters
PID myPID(&PID_input, &PID_output, &PID_setpoint, Kp, Ki, Kd, DIRECT);


#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
//OneWire oneWire1(ONE_WIRE_BUS_2);
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);


// LEDs
#include <Adafruit_NeoPixel.h>
#define LED_PIN 4
#define NUMPIXELS  12
Adafruit_NeoPixel LED = Adafruit_NeoPixel(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);
// starting LED colour
int r=20, g=20, b=20;


//motor controls
#include <Stepper.h>
// controls the heating 
#define HEATER_PIN 3
#define END_STOP_PIN A0
int end_stop = 0;
Stepper small_stepper(32, 6, 8, 7, 9);
int speed = 500;
// DEBUG: this is wrong
int absolute_pos = 0;


// global varialbes for the code
String serial_input;
float temperature;
unsigned long time;
float starting_time;
// gap between each measurment and adjustment in seconds
#define delay_time 0.02


void setup(void){
  // start serial port
  Serial.begin(9600);
  Serial.setTimeout(50);

  //init the LED_RING, but not shining 
  LED.begin();
  LED_colour(0,0,0);
  // Heater
  sensors.begin();
  pinMode(HEATER_PIN, OUTPUT);
  // PID control for heater
  myPID.SetMode(AUTOMATIC);
  PID_setpoint = 37.5;  //set the temperature
  myPID.SetOutputLimits(1, 255);
  // home stage for accurate absolute_pos
  Serial.println("Recommand to home the stage if this is the first run");
  // home_stage();
  // move to the optimal position 
  // move_stage(3000,speed);
  // measure a starting time
  starting_time = float(millis())/float(1000);
  }

void loop(void){
  // To read serial input
  if (Serial.available()) {
    serial_input = Serial.readString();
    serial_condition(serial_input);  
    }

  // call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  sensors.requestTemperatures(); // Send the command to get temperatures
  double sensor_temp = sensors.getTempCByIndex(0);
  PID_input = sensor_temp;

  // when sensor disconnect, it gives a strange value
  if (sensor_temp < -50) {
    Serial.println("Sensor disconnected, incubator off");
    analogWrite(HEATER_PIN, 0);
  }
  else {
    myPID.Compute();
    analogWrite(HEATER_PIN, PID_output);
    
    //prints time since program started
    float time;
    time = float(millis())/float(1000);
    time = time - starting_time;
    Serial.print(time);   
    Serial.println(" s");
    // temeperature  
    Serial.print(sensor_temp);
    Serial.println(" *C");
    Serial.print("Heating effort is: ");
    Serial.println(PID_output);
  }
  delay(delay_time*1000);
}



void serial_condition(String serial_input){
  //Serial.println(serial_input);
  // trim is needed as there is blank space and line break
  serial_input.trim();
  
  if (serial_input == "led_on" or serial_input == "LED_on" ){
  // turn off the incubator to prevent current spike
  analogWrite(HEATER_PIN, 0);
  LED_colour(r,g,b);
  Serial.println("lights on");
  }
  else if (serial_input == "led_off" or serial_input == "LED_off"){
    LED_colour(0,0,0);
    Serial.println("lights off");
  }
  // move=600 
  // positive is toward the camera, negative is toward the endstop
  else if (serial_input.substring(0,4) == "move"){
    Serial.print("Move by: ");
    Serial.println(serial_input.substring(5).toFloat());
    int distance = serial_input.substring(5).toFloat();
    move_stage(distance, speed);
  }

  // speed=500
  else if (serial_input.substring(0,5) == "speed"){
    Serial.print("Changing the speed to: ");
    Serial.println(serial_input.substring(6).toFloat());
    speed = serial_input.substring(6).toFloat();
    if(speed==0){
      speed=250;
    }
    small_stepper.setSpeed(speed);
  }

  else if(serial_input == "pos"){
    Serial.print("Current position is: ");
    Serial.println(absolute_pos);
  }

    else if(serial_input == "stop"){
      small_stepper.setSpeed(250);
      small_stepper.step(0);
  }

  //
  else if(serial_input == "home"){
    Serial.println("homing");
    home_stage();
  }

  // LED_RGB=255,255,255
  else if (serial_input.substring(0,7) == "LED_RGB" or serial_input.substring(0,7) == "LED_rgb"){
    serial_input = serial_input.substring(8);
    r = (getValue(serial_input, ',', 0).toInt());
    g = (getValue(serial_input, ',', 1).toInt());   // turn the LED on (HIGH is the voltage level
    b = (getValue(serial_input, ',', 2).toInt());   // turn the LED on (HIGH is the voltage level
    LED_colour(r,g,b);
  }

  // temp=37
  else if (serial_input.substring(0,4) == "temp"){
    PID_setpoint = serial_input.substring(5).toFloat();
    if(PID_setpoint>50){
      Serial.println("Maximum temperature is 50 C");
      PID_setpoint = 50;
    }
    Serial.print("Temperature is set to ");
    Serial.print(PID_setpoint);
    Serial.println(" C");
  }
}



void LED_colour(int r, int g, int b) {
    for (int i = 0; i < NUMPIXELS; i++) {
      // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
      LED.setPixelColor(i, LED.Color(r, g, b)); // Moderately bright green color.
      LED.show(); // This sends the updated pixel color to the hardware.
      delay(5);
    }
}


void move_stage(float distance, float speed) {
   // turn off the incubator to prevent current spike
    analogWrite(HEATER_PIN, 0);
    if (distance < 0 && digitalRead(END_STOP_PIN) == LOW) {
      // if hit end_stop, and still trying to move upward
      Serial.println("already at the end stop");
      absolute_pos = 0;
    }
    else {
      small_stepper.setSpeed(speed);
      small_stepper.step(distance);
    }
    absolute_pos = absolute_pos + distance;
    Serial.println("done");
    Serial.print("Absolute position: ");
    Serial.println(absolute_pos);
}



void home_stage() {
  while (digitalRead(END_STOP_PIN) == HIGH) {
      // home at a defined speed?
      Serial.println("Homing stage, please wait ");
      move_stage(-500, 1000);
  }
  Serial.println("Stage homed, reset the absolute position");
  // after hitting the end_stop, reset the absolute position
  move_stage(0,speed); //default position
  absolute_pos = 0;
}




// sammy's home made code
String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
