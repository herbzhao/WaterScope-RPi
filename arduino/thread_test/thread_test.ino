#include <Thread.h>
#include <ThreadController.h>
#include <AccelStepper.h>
AccelStepper stepper_optics(AccelStepper::FULL4WIRE, 11, 13, 12, 10);
AccelStepper stepper_carousel(AccelStepper::FULL4WIRE, 7, 9, 8, 6);


// ThreadController that will controll all threads
ThreadController controll = ThreadController();


Thread myThread = Thread();
Thread hisThread = Thread();

float starting_time;


String serial_input = "...";
bool ledStatus = true;
float sensor_temps[10]; 


// callback for myThread
void niceCallback(){
//  Serial.print(serial_input);
//  Serial.println(millis());

String test_string = "move_opt=600";
Serial.println(test_string.substring(0, 4));
Serial.println(test_string.substring(5, 8));
Serial.println(test_string.substring(9));

  
}

// callback for hisThread
void blinkLed(){
  // static variables persist beyond the function call, preserving their data between function calls.
  static bool ledStatus = false;
  ledStatus = !ledStatus;

  digitalWrite(LED_BUILTIN, ledStatus);
  int j = 5;
  Serial.println("Average sensor: " + String(123) + "°C");
  Serial.println(char(194));

    stepper_carousel.setAcceleration(2000);
    stepper_carousel.setMaxSpeed(500.0);
    stepper_carousel.move(500);
    stepper_carousel.run();

 }


void setup(){
  Serial.begin(9600);

  pinMode(LED_BUILTIN, OUTPUT);
  starting_time = millis();

  // Configure myThread
  myThread.onRun(niceCallback);
  myThread.setInterval(800);

  // Configure myThread
  //hisThread.onRun(blinkLed);
  //hisThread.setInterval(500);

  // Adds both threads to the controller
  controll.add(&myThread);
  //controll.add(&hisThread); // & to pass the pointer to it


}

void loop(){
  // Rest of code
  if (Serial.available()) {
  // https://stackoverflow.com/questions/42863973/arduino-readstring-code-runs-slow
  // readString is slow
  serial_input = Serial.readStringUntil('\n');
  }

     
  // run ThreadController
  // this will check every thread inside ThreadController,
  // if it should run. If yes, he will run it;
  
  controll.run();
  blinkLed();
  delay(5000);
      

}
