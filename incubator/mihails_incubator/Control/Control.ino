#include <OneWire.h>
#include <DallasTemperature.h>

int dirA = 12;
int dirB = 13;

int pwmA = 3;
int pwmB = 11;

int oneWireBus = 4;

float avgT = 0;
float targetT = 37.5;
float diff = 0;

int power = 0;

int incoming = 0;

OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);


void setup() {
  pinMode(dirA, OUTPUT);
  pinMode(dirB, OUTPUT);
  pinMode(pwmA, OUTPUT);
  pinMode(pwmB, OUTPUT);

  digitalWrite(dirA, HIGH);
  digitalWrite(dirB, HIGH);

  analogWrite(pwmA, 0);
  analogWrite(pwmB, 0);

  Serial.begin(9600);
  sensors.begin();
}

void loop() {
  sensors.requestTemperatures();
  avgT = sensors.getTempCByIndex(0);

  power = max( min( int((targetT - avgT) * 128), 255), 0 );
  analogWrite(pwmA, power);
  analogWrite(pwmB, power);
//  Serial.println(avgT);
  if (Serial.available() > 0){
    incoming = Serial.parseInt();
    if (incoming == 13){
      Serial.println(avgT);
    }
    }
}

