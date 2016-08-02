//This is a arduino code allowing serial communication from computer
//It has so far intergrated with digitial write (dwp+pin#+on/off), analoge write(awp+pin#+0-255)
//controlling potentiometer(MCP series), reading voltage(output on serial monitor), etc.


//Prep for potentiometer
#include <SPI.h>
#include <mcp4xxx.h>
using namespace icecave::arduino;
MCP4XXX* pot;
float set_voltage;

//Setup onewire for temperatuer sensor
#include <OneWire.h>
#include <DallasTemperature.h>
// Data wire is plugged into pin 2 on the Arduino
#define ONE_WIRE_BUS 3

// Setup a oneWire instance to communicate with any OneWire devices 
OneWire oneWire(ONE_WIRE_BUS);
 
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);



// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:

  //connect Potentiometer at chip select (SS) pin at 10
  pot = new MCP4XXX(10);
  //set to 0V at P0A
  pot->set(pot->max_value());


  // Start up the onewire library
  sensors.begin();

  //initilise serial input
  Serial.begin(9600);
  Serial.end();
  Serial.begin(9600);
  //this speed up the String input = Serial.readString();
  Serial.setTimeout(150);
}


// the loop routine runs over and over again forever:
void loop() {
  voltage_read(0);
  serial_command();
  delay(100);
//  float sensor_temp = temp_read();
//  temp_control(sensor_temp, 30);
}


void voltage_read(int pin){

  // read the input on analog pin 0:
  int sensorValue = analogRead(pin);
  // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  float voltage = sensorValue * (5.0 / 1023.0);
  // print out the value you read:
  //print voltage line by line
  
  Serial.print("pin");
  Serial.print("A");
  Serial.print(pin);
  Serial.print(":  ");
  Serial.print(voltage);
  Serial.print("V \n \r");
}



//set pot to any number
void SetPot(){
  pot->set(set_voltage);
}

//Receive command from serial
void serial_command(){
  //read command from web interface
  String input = Serial.readString();
  String pre_command=input.substring(0,3); // first 3 letter

  //analog read pin  type "arp1"
  if (pre_command == "arp") {
    int pin_number = input.substring(3,5).toInt();
    voltage_read(pin_number);
  }

  //digital read pin type "drp1"
  if (pre_command == "drp") {
    int pin_number = input.substring(3,5).toInt();
    pinMode(pin_number, OUTPUT);
    digitalRead(pin_number);
    //need a function for this
  }
  
  //digital write any pins  "dwp03on or dwp03off"
  if (pre_command == "dwp") {
    int pin_number = input.substring(3,5).toInt();
    String pin_switch = input.substring(5);
    
    if (pin_switch == "on") {
      pinMode(pin_number, OUTPUT);
      digitalWrite(pin_number, HIGH);
    }  
    if (pin_switch == "off") {
      pinMode(pin_number, OUTPUT);
      digitalWrite(pin_number, LOW);
    }
  }

  //analog write pin "awp07255"
  if (pre_command == "awp") {
    int pin_number = input.substring(3,5).toInt();
    int analog_value = input.substring(5).toInt();
      pinMode(pin_number, OUTPUT);
      analogWrite(pin_number,analog_value);
  }


    //Control potentiometer: type pot+value (voltage)
  if (pre_command == "pot") {
    String pot_command = input.substring(3); //after 3 letters
    float set_voltage = 256-pot_command.toFloat()*256/5;
    SetPot();
  }

    //analog pin control "RGB255255255"
  if (pre_command == "RGB") {
    int r_value = input.substring(3,6).toInt();
    int g_value = input.substring(6,9).toInt();
    int b_value = input.substring(9,12).toInt();
      pinMode(05, OUTPUT); //red
      analogWrite(05,r_value);
      pinMode(06, OUTPUT); //red
      analogWrite(06,g_value);
      pinMode(07, OUTPUT); //red
      analogWrite(07,b_value);
      
  }
}  




float temp_read(){
  // call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  sensors.requestTemperatures(); // Send the command to get temperatures
  float sensor_temp = sensors.getTempCByIndex(0);
  Serial.print("Temperature for Device 1 is: ");
  Serial.println(sensor_temp); // Why "byIndex"? 
    // You can have more than one IC on the same bus. 
    // 0 refers to the first IC on the wire
  return sensor_temp;
}

void temp_control(float sensor_temp, float set_temp){
  if (sensor_temp < set_temp) {
      pinMode(4, OUTPUT); 
      digitalWrite(4, HIGH);
      Serial.println("heating");
  }
  if (sensor_temp >= set_temp) {
      pinMode(4, OUTPUT);
      digitalWrite(4, LOW);
      Serial.println("cooling");
  }
}


