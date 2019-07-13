#include <Thread.h>
#include <ThreadController.h>

// ThreadController that will controll all threads
ThreadController controll = ThreadController();


Thread myThread = Thread();
Thread hisThread = Thread();

String serial_input = "...";
bool ledStatus = true;


// callback for myThread
void niceCallback(){
  Serial.print(serial_input);
  Serial.println(millis());
}

// callback for hisThread
void blinkLed(){
  // static variables persist beyond the function call, preserving their data between function calls.
  static bool ledStatus = false;
  ledStatus = !ledStatus;

  digitalWrite(LED_BUILTIN, ledStatus);

  Serial.print("blinking: ");
  Serial.println(ledStatus);
}


void setup(){
  Serial.begin(9600);

  pinMode(LED_BUILTIN, OUTPUT);

  // Configure myThread
  myThread.onRun(niceCallback);
  myThread.setInterval(1000);

  // Configure myThread
  hisThread.onRun(blinkLed);
  hisThread.setInterval(500);

  // Adds both threads to the controller
  controll.add(&myThread);
  controll.add(&hisThread); // & to pass the pointer to it
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


}
