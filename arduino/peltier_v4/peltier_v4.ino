// PID_AutoTune_v0 - Version: Latest 
#include <PID_v1.h>
#include <PID_AutoTune_v0.h>
double PID_setpoint, PID_input, PID_output;
//Define the aggressive and conservative Tuning Parameters
// https://robotics.stackexchange.com/questions/9786/how-do-the-pid-parameters-kp-ki-and-kd-affect-the-heading-of-a-differential
double Kp=1000, Ki=50, Kd=50;
//Specify the links and initial tuning parameters
PID myPID(&PID_input, &PID_output, &PID_setpoint, Kp, Ki, Kd, REVERSE);

// peltier
#define peltier_pin 9    // LED connected to digital pin 9

// LEDs
#include <Adafruit_NeoPixel.h>
#define LED_PIN 6
#define num_LEDs 12
Adafruit_NeoPixel LEDs = Adafruit_NeoPixel(num_LEDs, LED_PIN, NEO_GRB + NEO_KHZ800);
// starting LED colour
int r=255, g=255, b=255;

// Thermistor
// which analog pin to connect
#define thermistor_pin A0         
// temp. for nominal resistance (almost always 25 C)
#define temperature_norminal 25   
// resistance at 25 degrees C
#define thermistor_norminal_resistance 10000   
// The beta coefficient of the thermistor (usually 3000-4000)
#define B_coefficient 3435
// the value of the serial resistor
#define reference_resistor 10000    
// how many analogue_readings to take and average, more takes longer
// but is more 'smooth'
#define number_of_analogue_measurements 10
// set some variables for thermistor
uint16_t analogue_readings[number_of_analogue_measurements];
uint8_t index_k;
float average_analogue_reading;


// global varialbes for the code
String serial_input;
float temperature;
// gap between each measurment and adjustment in seconds
#define delay_time 0.2

// Average the temperature measurement to ensure a stable temperature control
#define number_of_temp_measurements 10
int index_i = 1;
float temperature_sum;
float temperature_ave;

// final goal of temperature
#define PID_default_starting_setpoint 23
#define PID_default_final_setpoint 18
#define phase_change_point 21
float PID_final_setpoint;
// starting the arduino with cooling or not?
bool cooling = false;
// this is the step that PID setpoint change each time 
// (smaller = longer = less overshoot)
#define PID_setpoint_change_step 0.2
// this is temperature fluctuation range that is acceptable before changing PID_setpoint
// (smaller = longer time to reach stability = less chance of false positive )
#define PID_fluctuation_range 0.05


void setup(void) {
  // start serial port
  Serial.begin(9600);
  Serial.setTimeout(50);
  
  //initialize the variables we're linked to
  PID_setpoint = PID_default_starting_setpoint;
  PID_final_setpoint = PID_default_final_setpoint;
  myPID.SetOutputLimits(0, 255);

  //turn the PID on
  myPID.SetMode(AUTOMATIC);
  
  //start the LED
  LEDs.begin();
  LED_colour(r,g,b);
}


void loop(void) {
  PID_input = read_temperature();
  
  // check if the average temperature is stable within range
  // then adjust PID_setpoint with small step to prevent overshoot
  if (cooling == true){
    measure_average_temp_and_adjust_PID_setpoint();
    
    // TODO: a way to control cooling rate? C/min
    
    // PID control the peltier cooling effort
    myPID.Compute();
    analogWrite(peltier_pin, PID_output);
  }
  else if (cooling == false){
    // if not cooling, send no current to peltier
    analogWrite(peltier_pin, 0);
  }

  // To read serial input
  if (Serial.available()) 
  {
    serial_input = Serial.readString();
    serial_condition(serial_input);  
  }

  // wait for next temperature measurement
  delay(delay_time*1000);
}



void measure_average_temp_and_adjust_PID_setpoint(){
  if ( index_i < number_of_temp_measurements){
    temperature_sum+= PID_input;
    index_i += 1;
    // Serial.println("sum temperature is:");
    // Serial.println(temperature_sum);
  }
  else{
    temperature_sum+= PID_input;
    temperature_ave = temperature_sum/number_of_temp_measurements;
    // Serial.print("temperature average is :");
    // Serial.println(temperature_ave);
    adjust_PID_setpoint();
    // Serial.println("averaging the temperature and adjust PID setpoint");
    // reset the index and temperature_sum
    index_i = 1;
    temperature_sum = 0;
  }
}




float read_temperature(){
  // take N analogue_readings in a row, with a slight delay
  for (index_k=0; index_k< number_of_analogue_measurements; index_k++) {
    analogue_readings[index_k] = analogRead(thermistor_pin);
    delay(10);
  }
 
  // average all the analogue_readings out
  average_analogue_reading = 0;
  for (index_k=0; index_k< number_of_analogue_measurements; index_k++){
    average_analogue_reading += analogue_readings[index_k];
  }
  average_analogue_reading /= number_of_analogue_measurements;
  
  // convert the voltage value to resistance
  average_analogue_reading = 1023 / average_analogue_reading - 1;
  average_analogue_reading = reference_resistor / average_analogue_reading;
  temperature = average_analogue_reading / thermistor_norminal_resistance;     // (R/Ro)
  temperature = log(temperature);                  // ln(R/Ro)
  temperature /= B_coefficient;                   // 1/B * ln(R/Ro)
  temperature += 1.0 / (temperature_norminal + 273.15); // + (1/To)
  temperature = 1.0 / temperature;                 // Invert
  temperature -= 273.15;                         // convert to C
  
  // also get a time variable
  float time;
  time = float(millis())/float(1000);
  Serial.print(time);    //prints time since program started
  Serial.println(" s");

  // temeperature  
  Serial.print(temperature);
  Serial.println(" *C");
  
  // return value
  return temperature;
}


// move the temperature down slowly to ensure a smooth curve?
void adjust_PID_setpoint() {
  // Serial.println("comparing the temp_ave and PID_setpoint");
  // when temperature stablise then reduce setpoint again
  if (abs(temperature_ave-PID_setpoint)< PID_fluctuation_range){
    // only move the setpoint if it is not the final_setpoint
    // It is not easy to compare float with == or !=
    // we use larger or smaller than our jumping step to test whether they are equal
    // convert float into int and then compare
    if (abs(PID_setpoint - PID_final_setpoint) > float(PID_setpoint_change_step)/2){
      // decrease the setpoint by tiny bit each time
      PID_setpoint = PID_setpoint- PID_setpoint_change_step;
      // Serial.println("moving PID_setpoint by one step");
      // Serial.println("current PID_setpoint and PID_final_setpoint are");
      // Serial.print(PID_setpoint);
      // Serial.println(PID_final_setpoint);
    }
    else{
      // Serial.println("Reached the designated temperature");
    }
  }
  //Serial.print("Current PID_setpoint is:");
  //Serial.println(PID_setpoint);
}


void serial_condition(String serial_input){
  //Serial.println(serial_input);
  // trim is needed as there is blank space and line break
  serial_input.trim();
  if (serial_input == "66" or serial_input == "led_on"){
    LED_colour(255,255,255);
  }
  else if (serial_input == "-66" or serial_input == "led_off"){
    LED_colour(0,0,0);
  }
  else if (serial_input == "stop" or serial_input == "heat"){
    Serial.println("stop cooling");
    cooling = false;
  }
  else if (serial_input == "restart" or serial_input == "cool"){
    Serial.println("start the cooling procedure from the beginning");
    PID_setpoint = PID_default_starting_setpoint;
    PID_final_setpoint = PID_default_final_setpoint;
    cooling = true;
  }
  else if (serial_input == "hold"){
    Serial.println("hold at current temperature");
    cooling = true;
    PID_final_setpoint = temperature;
    PID_setpoint = PID_final_setpoint;
  }
  else if (serial_input == "prepare"){ 
    Serial.println("cool down the droplets right before the shape changing");
    cooling = true;
    PID_final_setpoint = phase_change_point;
    // if it is already too cold, heat up to the point
    if (PID_setpoint < PID_final_setpoint){
      PID_setpoint = PID_final_setpoint;
    }
  }
  else if (serial_input == "continue"){
    Serial.println("start the cooling procedure from the current temperature");
    // dont change the current setpoint, but change the final_setpoint
    PID_final_setpoint = PID_default_final_setpoint;
    cooling = true;
  }
}


void LED_colour(int r, int g, int b) {
  for (int i = 0; i < num_LEDs; i++) {
    // LED.Color takes RGB values, from 0,0,0 up to 255,255,255
    LEDs.setPixelColor(i, LEDs.Color(r, g, b)); // Moderately bright green color.
    LEDs.show(); // This sends the updated pixel color to the hardware.
    delay(5);
  }
}
