// PID_AutoTune_v0 - Version: Latest 
#include <PID_v1.h>
//#include <PID_AutoTune_v0.h>
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
int r=30, g=30, b=30;

// Thermistor
// which analog pin to connect
#define thermistor_pin A0         
// temp. for nominal resistance (almost always 25 C)
#define temperature_norminal 25   
// resistance at 25 degrees C
#define thermistor_norminal_resistance 100000   
// The beta coefficient of the thermistor (usually 3000-4000)
#define B_coefficient 3950
// the value of the serial resistor
#define reference_resistor 100000    
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
float starting_time;
// gap between each measurment and adjustment in seconds
#define delay_time 0.2

// Average the temperature measurement to ensure a stable temperature control
#define number_of_temp_measurements 30
int index_i = 1;
float temperature_sum;
float temperature_ave;

// final goal of temperature
// CHANGE: this is used to offset depending on the sample position, sensor position, etc.
#define temp_offset 0
float PID_default_starting_setpoint = 21 + temp_offset;
float PID_default_final_setpoint = 17 + temp_offset;
float PID_prep_setpoint = 22 + temp_offset;

float PID_final_setpoint;
// starting the arduino with cooling or not?
bool cooling = false;
// this is the step that PID setpoint change each time 
// (smaller = longer = less overshoot)
float PID_setpoint_change_step = 0.2
;
// this is temperature fluctuation range that is acceptable before changing PID_setpoint
// (smaller = longer time to reach stability = less chance of false positive )
float PID_fluctuation_range = 0.05;



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
  
  // measure a starting time
  starting_time = float(millis())/float(1000);
}


void loop(void) {
  PID_input = read_temperature();
  
  // check if the average temperature is stable within range
  // then adjust PID_setpoint with small step to prevent overshoot
  if (cooling == true){
    measure_average_temp_and_adjust_PID_setpoint();
    
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
  time = time - starting_time;
  
  Serial.print(time);    //prints time since program started
  Serial.println(" s");

  // temeperature  
  Serial.print(temperature);
  Serial.println(" *C");
  
  // return value
  return temperature;
}


// automatically adjust the setpoint from the PID_setpoint to the PID_final_setpoint
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
  else if (serial_input == "restart"){
    Serial.println("start the cooling procedure using the default values");
    PID_setpoint = PID_default_starting_setpoint;
    PID_final_setpoint = PID_default_final_setpoint;
    cooling = true;
  }
  else if (serial_input == "continue" or serial_input == "start" or serial_input == "cool"){
    Serial.println("start the cooling procedure using previously specified Temps or default");
    // cool to PID_setpoint and then move slowly towards PID_final_setpoint
    // the PID_final_setpoint can be a new value (if defined)
    PID_setpoint = temperature;
    PID_final_setpoint = PID_default_final_setpoint;
    cooling = true;
  }
  else if (serial_input == "prepare"){ 
    Serial.print("equilibriate to the droplets right before the shape changing");
    Serial.println(PID_prep_setpoint);
    PID_setpoint = PID_prep_setpoint;
    PID_final_setpoint = PID_prep_setpoint;
    cooling = true;
  }
  //goto=15
  else if (serial_input.substring(0,4) == "goto"){ 
    Serial.print("Go to temperature: ");
    float temperature_input = serial_input.substring(5).toFloat();
    Serial.println(temperature_input);
    PID_setpoint = temperature_input;
    PID_final_setpoint = temperature_input;
    cooling = true;
  }
  else if (serial_input == "hold"){
    Serial.println("hold at current temperature");
    PID_final_setpoint = temperature;
    PID_setpoint = temperature;
    cooling = true;
  }
// T_start=24
  else if (serial_input.substring(0,6) == "Tstart"){
    Serial.print("changing the starting temperature: ");
    float temperature_input = serial_input.substring(7).toFloat();
    Serial.println(temperature_input);
    PID_default_starting_setpoint = temperature_input;
  }
  // T_fin=19
  else if (serial_input.substring(0,4) == "Tfin"){
    Serial.print("changing the finishing temperature: ");
    float temperature_input = serial_input.substring(5).toFloat();
    Serial.println(temperature_input);
    PID_default_final_setpoint = temperature_input;
  }
  
  // T_prep=25
  else if (serial_input.substring(0,5) == "Tprep"){
    Serial.print("changing the prepare temperature: ");
    float temperature_input = serial_input.substring(6).toFloat();
    Serial.println(temperature_input);
    PID_prep_setpoint = temperature_input;
  }
  // PID_step=0.1
  else if (serial_input.substring(0,8) == "PID_step"){
    Serial.print("Changing the PID steps, this will affect slope: ");
    Serial.println(serial_input.substring(9).toFloat());
    PID_setpoint_change_step = serial_input.substring(9).toFloat();
  }
  
  // PID=1000,50,50
  else if (serial_input.substring(0,3) == "PID"){
    serial_input = serial_input.substring(4);
    Kp = (getValue(serial_input, ',', 0).toInt());
    Ki = (getValue(serial_input, ',', 1).toInt());   // turn the LED on (HIGH is the voltage level
    Kd = (getValue(serial_input, ',', 2).toInt());   // turn the LED on (HIGH is the voltage level
    Serial.print("New PID value: ");
    Serial.print(Kp);
    Serial.print(", ");
    Serial.print(Ki);
    Serial.print(", ");
    Serial.println(Kd);
  }
  // LED_RGB=255,255,255
  else if (serial_input.substring(0,7) == "LED_RGB" or serial_input.substring(0,7) == "LED_rgb"){
    serial_input = serial_input.substring(8);
    r = (getValue(serial_input, ',', 0).toInt());
    g = (getValue(serial_input, ',', 1).toInt());   // turn the LED on (HIGH is the voltage level
    b = (getValue(serial_input, ',', 2).toInt());   // turn the LED on (HIGH is the voltage level
    LED_colour(r,g,b);
  }
  else if (serial_input == "reset_time"){
    starting_time = float(millis())/float(1000);
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
