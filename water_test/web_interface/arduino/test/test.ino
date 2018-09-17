//int incomingByte = 0;
String Serial_input;

void setup(){
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop(){
  Serial.println("what");
  
  if (Serial.available()) {
  Serial_input = Serial.readString();
  condition(Serial_input);  
  }
  delay(500);
}

void condition(String Serial_input){
  Serial.println(Serial_input);
  // trim is needed as there is blank space and line break
  Serial_input.trim();
  if (Serial_input == "66")
  {
    Serial.println("lights on");
    digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  }
  else if (Serial_input == "-66")
  {
    Serial.println("lights off");
    digitalWrite(LED_BUILTIN, LOW);   // turn the LED on (HIGH is the voltage level)
  }
  else
  {
    Serial.println("Moving stage");
    Serial.println(Serial_input.toInt());   // turn the LED on (HIGH is the voltage level)
  }
}