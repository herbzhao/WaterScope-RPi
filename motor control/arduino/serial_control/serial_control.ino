String income_string;
void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);      // open the serial port at 9600 bps:    
  Serial.setTimeout(50);
}

void loop() {
  // put your main code here, to run repeatedly:
  income_string = Serial.readString();
  if ( income_string == "x"){
    Serial.println("hello world");
  }
  if (income_string == "G01 X20 F200") {
      digitalWrite(LED_BUILTIN, HIGH);    // turn the LED off by making the voltage LOW
  }

  if (income_string == "G01 Y-20 F200") {
      digitalWrite(LED_BUILTIN, LOW);   // turn the LED on (HIGH is the voltage level)
      
  }
}
