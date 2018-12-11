
#include <EEPROM.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <PID_v1.h>
#include <Stepper.h>
#include <Adafruit_NeoPixel.h>

#ifdef __AVR__
#include <avr/power.h>
#endif

//NEW CONFIGURATION for incubator/leds
#define LED1 4
#define LED2 19
#define CONTROL_PIN 3
#define ONE_WIRE_BUS 2
#define END_STOP A0
#define PIN 4
#define NUMPIXELS      12

//motor controls
int end_stop = 0;
Stepper small_stepper(32, 6, 8, 7, 9);
int  Steps2Take;
int val = 1;
int led_flag = 0;
int previous_led = -256;

//Define Variables we'll be connecting to for PID temperature control
double Setpoint, Input, Output;



PID myPID(&Input, &Output, &Setpoint, 2, 5, 1, DIRECT);
OneWire oneWire(ONE_WIRE_BUS);
//OneWire oneWire1(ONE_WIRE_BUS_2);

// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

int delayval = 500; // delay for half a second
byte LED_flag = 0;
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
int incomingByte = 1;   // for incoming serial data
unsigned int counter = 0;
unsigned long time2 = 0;
unsigned long time3 = 0;
int red = 255;
int blue = 255;
int green = 255;
unsigned long time;
String Serial_input;
int absolute = 0;

void setup(void)
{
  // start serial port
  Serial.begin(9600);
  Serial.setTimeout(50);

  // Serial.println("Dallas Temperature IC Control Library Demo");
  // Start up the library
  sensors.begin();
  inputString.reserve(200);
  pinMode(CONTROL_PIN, OUTPUT);
  // pinMode(LED1,OUTPUT);
  pinMode(LED2, OUTPUT);
  //  digitalWrite(LED1,HIGH);
  digitalWrite(LED2, HIGH);
  LED(155,155,155);

  pinMode(6, OUTPUT);
  pinMode(5, OUTPUT);
  digitalWrite(6, LOW);
  digitalWrite(5, HIGH);
  // find_end();
  myPID.SetMode(AUTOMATIC);
  Setpoint = 37.5; //set the temperature
  myPID.SetOutputLimits(1, 255);
  myPID.SetTunings(18, 20, 1);
  //read where the next value should go and write a placeholder
  counter = EEPROMReadInt(0);
  EEPROMWriteInt(counter, 8000);
  counter = counter + 2;
  EEPROMWriteInt(0, counter);
  Serial.println(EEPROMReadInt(0));

  // End of trinket special code
  //setup LEDs to OFF at the start
  pixels.begin(); // This initializes the NeoPixel library.
  for (int i = 0; i < NUMPIXELS; i++) {
    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
    pixels.setPixelColor(i, pixels.Color(0, 0, 0)); // Moderately bright green color.
    pixels.show(); // This sends the updated pixel color to the hardware.
    delay(5); // Delay for a period of time (in milliseconds).
  }
}

void LED(int r, int g, int b) {
    for (int i = 0; i < NUMPIXELS; i++) {
      // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
      pixels.setPixelColor(i, pixels.Color(r, g, b)); // Moderately bright green color.
      pixels.show(); // This sends the updated pixel color to the hardware.
      delay(5);
    }
}

void loop(void)
{
  time = millis();
  if (Serial.available() >= 1) {
    Serial_input = Serial.readString();
    condition(Serial_input);
  }
  if ((time - time3) > 500){
    time3 = time;
  // call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  sensors.requestTemperatures(); // Send the command to get temperatures
  double sensor_temp = sensors.getTempCByIndex(0);
  Input = sensor_temp;
  if (sensor_temp == -127) {
    Serial.println("Sensor disconnected, incubator off");
    analogWrite(CONTROL_PIN, 0);
  }
  else {
//    if (sensor_temp > 36 && sensor_temp < 41) {
      //digitalWrite(12,LOW);
  //    Serial.write("Incubator ready. ");
    //}
    //else if (sensor_temp > 37 && sensor_temp < 38) {
     // Serial.write("Perfect temperature. ");
    //}
    //else {
      // digitalWrite(12,HIGH);
      //Serial.write("Incubator not ready. ");
    //}
    myPID.Compute();
    analogWrite(CONTROL_PIN, Output);
    Serial.print("Temperature is ");
    Serial.print(Input);
    Serial.print(" Heating effort is ");
    Serial.println(Output);
  }
  }
  if ((time - time2) > 300000) {
    Serial.println("temperature written to disk");
    EEPROMWriteInt(counter, int(Input * 100));
    counter = counter + 2;
    EEPROMWriteInt(0, counter);
    time2 = time;
    if (counter > 1020) {
      counter = 2;
      EEPROMWriteInt(0, counter);
    }
  }
}

void EEPROMWriteInt(int p_address, int p_value)
{
  byte lowByte = ((p_value >> 0) & 0xFF);
  byte highByte = ((p_value >> 8) & 0xFF);
  EEPROM.write(p_address, lowByte);
  EEPROM.write(p_address + 1, highByte);
}

//This function will read a 2 byte integer from the eeprom at the specified address and address + 1
unsigned int EEPROMReadInt(int p_address)
{
  byte lowByte = EEPROM.read(p_address);
  byte highByte = EEPROM.read(p_address + 1);
  return ((lowByte << 0) & 0xFF) + ((highByte << 8) & 0xFF00);
}

void find_end() {
  while (end_stop == 0) {
    if (digitalRead(END_STOP) == HIGH) {
      small_stepper.setSpeed(350);
      small_stepper.step(-256);
    }
    else {
      end_stop = 1;
    }
  }
  small_stepper.setSpeed(700);
  small_stepper.step(0); //default position
  absolute = 0;
}


void condition(String Serial_input){
  // trim is needed as there is blank space and line break
  char first;
  first = Serial_input[0];
  Serial_input[0] = ' ';
  Serial_input.trim();
  if (Serial_input == "ed_on")
  {
    analogWrite(CONTROL_PIN, 0);
    led_flag = 1;
    LED(red,green,blue);
    Serial.println("lights on");
  }
  else if (Serial_input == "ed_off")
  {
    led_flag = 0;
    LED(0,0,0);
    Serial.println("lights off");
  }
  else if (first == 'C'){
    Serial.print("New RGB: ");
    red = (getValue(Serial_input, ',', 0).toInt());
    green = (getValue(Serial_input, ',', 1).toInt());   // turn the LED on (HIGH is the voltage level
    blue = (getValue(Serial_input, ',', 2).toInt());   // turn the LED on (HIGH is the voltage level
    Serial.print(red);Serial.print(",");Serial.print(green);Serial.print(",");Serial.println(blue);
  }
  else if(first == 'M')
  {
    Serial.println("Moving");
    int pos = (getValue(Serial_input, ',', 0).toInt());   // turn the LED on (HIGH is the voltage level
    int speeed (getValue(Serial_input, ',', 1).toInt());   // turn the LED on (HIGH is the voltage level
    if(speeed==0){
      speeed=250;
    }
     analogWrite(CONTROL_PIN, 0);
      small_stepper.setSpeed(speeed);
      if (val < 0 && digitalRead(END_STOP) == LOW) {
      }
      else {
        if (led_flag == 1) {
          small_stepper.step(pos);
        }
        else {
          small_stepper.step(pos);
        }
      }
      absolute = absolute + pos;
      Serial.println("done");
      Serial.print("Absolute position: ");
      Serial.println(absolute);
  }
  else if(first == 'H'){
    find_end();
    Serial.println("homing");
  }
  else if(first == 'T'){
    Setpoint = (getValue(Serial_input, ',', 0).toFloat());
    if(Setpoint>50){
      Setpoint = 50;
      Serial.println("Maximum temperature is 50 C");
    }
    Serial.print("Temperature is set to ");
    Serial.print(Setpoint);
    Serial.println(" C");
  }
  else {
    Serial.println("invalid command");
  }
}

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

