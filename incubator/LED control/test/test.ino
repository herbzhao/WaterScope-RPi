#include <OneWire.h>
#include <DallasTemperature.h>
 
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
// Data wire is plugged into pin 2 on the Arduino
#define ONE_WIRE_BUS 10
#define CONTROL_PIN 2
#define PIN            6
#define NUMPIXELS      8

// Setup a oneWire instance to communicate with any OneWire devices 
// (not just Maxim/Dallas temperature ICs)
float threshold = 37.5;

OneWire oneWire(ONE_WIRE_BUS);
 
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);
 Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

int delayval = 500; // delay for half a second
byte LED_flag = 1;
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
int incomingByte = 1;   // for incoming serial data

void setup(void)
{
  // start serial port
  Serial.begin(9600);
  Serial.setTimeout(50);
  Serial.println("Dallas Temperature IC Control Library Demo");
  // Start up the library
  sensors.begin();
  inputString.reserve(200);
  pinMode(CONTROL_PIN,OUTPUT);
  #if defined (__AVR_ATtiny85__)
  if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
#endif
  // End of trinket special code

  pixels.begin(); // This initializes the NeoPixel library.
  for(int i=0;i<NUMPIXELS;i++){

    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
    pixels.setPixelColor(i, pixels.Color(255,0,0)); // Moderately bright green color.

    pixels.show(); // This sends the updated pixel color to the hardware.

    delay(delayval); // Delay for a period of time (in milliseconds).

  }
}
 
 
void loop(void)
{
          // send data only when you receive data:
        if (Serial.available() > 0) {
                // read the incoming byte:
                incomingByte = Serial.read();

                // say what you got:
                
          if(incomingByte == 0)
          {
            Serial.println("LED OFF");
            LED_flag = 48;
          }
          else
          {
            Serial.println("LED ON");
            LED_flag = 1;
          }
        }

  // call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  sensors.requestTemperatures(); // Send the command to get temperatures
  float sensor_temp = sensors.getTempCByIndex(0);
  float sensor_temp_2 = sensors.getTempCByIndex(1);
  Serial.print(sensor_temp);
  Serial.print(',');
  Serial.println(sensor_temp_2);
//  Serial.print("Temperature for Device 2 is: ");
//  Serial.println(sensor_temp_2); // Why "byIndex"? 
  if(sensor_temp>threshold){
    analogWrite(CONTROL_PIN,0);
    Serial.print("cooling, temperature is ");
 //   Serial.println(sensor_temp); // Why "byIndex"? 

  }
  else {
    if (sensor_temp>36.8){
    analogWrite(CONTROL_PIN,80);
    }
    else {
       analogWrite(CONTROL_PIN,150);
    }
    if (sensor_temp<35){
    for(int i=0;i<NUMPIXELS;i++){

    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
    if (LED_flag==1){
    pixels.setPixelColor(i, pixels.Color(255,0,0)); // Moderately bright green color.
    }
    else {
      
    pixels.setPixelColor(i, pixels.Color(0,0,0)); // Moderately bright green color.
    }
    pixels.show(); // This sends the updated pixel color to the hardware.

    delay(5); // Delay for a period of time (in milliseconds).

  }
    }
    else {
       for(int i=0;i<NUMPIXELS;i++){

    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
    if (LED_flag==1){
    pixels.setPixelColor(i, pixels.Color(0,0,255)); // Moderately bright green color.
    }
    else {
      
    pixels.setPixelColor(i, pixels.Color(0,0,0)); // Moderately bright green color.
    }

    pixels.show(); // This sends the updated pixel color to the hardware.

    delay(5); // Delay for a period of time (in milliseconds).

  }
    }
    
   Serial.print("heating, temperature is ");
 //   Serial.println(sensor_temp); // Why "byIndex"? 
  }
    // You can have more than one IC on the same bus. 
    // 0 refers to the first IC on the wire
  delay(500);
}


