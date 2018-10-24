/*
  ReadAnalogVoltage

  Reads an analog input on pin 0, converts it to voltage, and prints the result to the Serial Monitor.
  Graphical representation is available using Serial Plotter (Tools > Serial Plotter menu).
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/ReadAnalogVoltage
*/

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

// the loop routine runs over and over again forever:
void loop() {
  // read the input on analog pin 0:
  float X_value = analogRead(A1) * (5.0 / 1023.0);
  float Y_value = analogR
  ead(A2) * (5.0 / 1023.0);
  float Z_value = analogRead(A3) * (5.0 / 1023.0);
  // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  // print out the value you read:
  Serial.print("X value: ");
  Serial.println(X_value);
  Serial.print("Y value: ");
  Serial.println(Y_value);
  Serial.print("Z value: ");
  Serial.println(Z_value);
  
  delay(100);
}

int number_of_analog_acceleration_measurements = 10;
uint16_t X_values[number_of_analog_acceleration_measurements];
uint16_t Y_values[number_of_analog_acceleration_measurements];
uint16_t Z_values[number_of_analog_acceleration_measurements];
uint8_t index_j;
float average_X_value;
float average_Y_value;
float average_Z_value;

float read_acceleration(){
  // take N analogue_readings in a row, with a slight delay
  for (index_j=0; index_j< number_of_analog_acceleration_measurements; index_j++) {

    X_values[index_j] = analogRead(A1);
    Y_values[index_j] = analogRead(A2);
    Z_values[index_j] = analogRead(A3);;
    delay(10);
  }
 
  // average all the analogue_readings out
  average_X_value = 0;
  average_Y_value = 0;
  average_Z_value = 0;
  
  for (index_j=0; index_j< number_of_analogue_measurements; index_j++){
    average_X_value += X_values[index_j];
    average_Y_value += Y_values[index_j];
    average_Z_value += Z_values[index_j];  
  }
  
  average_X_value = average_X_value / number_of_analogue_measurements  * (5.0 / 1023.0);
  average_Y_value = average_Y_value / number_of_analogue_measurements  * (5.0 / 1023.0);
  average_Z_value = average_Z_value / number_of_analogue_measurements  * (5.0 / 1023.0);
}