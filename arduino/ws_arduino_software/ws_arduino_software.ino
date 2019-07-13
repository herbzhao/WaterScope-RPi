#include <PID_v1.h>
double PID_setpoint, PID_input, PID_output;
//Define the aggressive and conservative Tuning Parameters
// https://robotics.stackexchange.com/questions/9786/how-do-the-pid-parameters-kp-ki-and-kd-affect-the-heading-of-a-differential
double Kp = 18, Ki = 1, Kd = 1;
//Specify the links and initial tuning parameters
PID myPID(&PID_input, &PID_output, &PID_setpoint, Kp, Ki, Kd, DIRECT);

#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
//OneWire oneWire1(ONE_WIRE_BUS_2);
// Pass our oneWire reference to Dallas Temperature.

// multiple sensors https://lastminuteengineers.com/multiple-ds18b20-arduino-tutorial/
DallasTemperature sensors(&oneWire);
int sensor_counts;

// LEDs
#include <Adafruit_NeoPixel.h>
#define LED_PIN 4
#define NUMPIXELS 12
Adafruit_NeoPixel LED = Adafruit_NeoPixel(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);
// starting LED colour
int r = 5, g = 5, b = 5;

//motor controls
#include <Stepper.h>
// controls the heating
#define HEATER_PIN 3
#define END_STOP_PIN A0
int end_stop = 0;
// the carousel rotatry motor
Stepper optics_stepper(32, 11, 13, 12, 10);
//  the optics stage motor pins
Stepper carousel_stepper(32, 7, 9, 8, 6);



int speed = 500;
// DEBUG: this is wrong
int absolute_pos = 0;

// Threading
#include <Thread.h>
#include <ThreadController.h>
// ThreadController that will controll all threads
ThreadController thread_controller = ThreadController();
Thread temp_thread = Thread();
Thread read_serial_thread = Thread();
Thread led_thread = Thread();
Thread optics_motor_thread = Thread();
Thread carousel_motor_thread = Thread();
// Thread hisThread = Thread();

// global varialbes for the code
String serial_input;
float starting_time;

void setup(void)
{
    // start serial port
    Serial.begin(9600);
    Serial.setTimeout(50);

    //init the LED_RING, but not shining
    LED.begin();
    LED_colour(0, 0, 0);
    // init the temperature sensors
    sensors.begin();
    sensor_counts = sensors.getDeviceCount();

    // init the heater PID
    pinMode(HEATER_PIN, OUTPUT);
    // PID control for heater
    myPID.SetMode(AUTOMATIC);
    PID_setpoint = 0; //set the temperature
    myPID.SetOutputLimits(1, 255);

    // Configure Threads
    temp_thread.onRun(read_temp_adjust_heating);
    temp_thread.setInterval(500);
    read_serial_thread.onRun(read_serial);
    read_serial_thread.setInterval(200);
    // Adds  threads to the controller
    thread_controller.add(&read_serial_thread); // & to pass the pointer to it
    thread_controller.add(&temp_thread); // & to pass the pointer to it

    Serial.println("Recommand to home the stage if this is the first run");
    // DEBUG: uncomment on deployment
    // home_stage();
    // move to the optimal position
    // move_stage(3000,speed);
    // measure a starting time
    starting_time = millis();
}

void loop(void)
{
  // run the threads
  thread_controller.run();
}

void read_serial(void){
    // To read serial input
    if (Serial.available())
    {
        // https://stackoverflow.com/questions/42863973/arduino-readstring-code-runs-slow
        // speed up the Serial.readString
        serial_input = Serial.readStringUntil('\n');
        serial_condition(serial_input);
    }
}

void read_temp_adjust_heating(void)
{
    // an array to record sensors temp
    float sensors_temp[sensor_counts];
    // declare relavent variables
    float temperature_sum = 0;
    float ave_temperature;
    // a variable to store error of the sensor connection
    bool sensors_error = false;

    // call sensors.requestTemperatures() to issue a global temperature
    // request to all devices on the bus
    sensors.requestTemperatures();

    //prints time since program started
    float time = (millis() - starting_time) / float(1000);
    Serial.println(String(time) + " s");
    // Iterate through multiple sensors 
    // Record and display temperature from each sensor
    for (int i = 0; i < sensor_counts; i++)
    {
        sensors_temp[i] = sensors.getTempCByIndex(i);
        // Serial.println("Sensor " + String(i + 1) + ": " + String(sensors_temp[i]) + " *C");
        temperature_sum += sensors_temp[i];
    }
    ave_temperature = temperature_sum / sensor_counts;
    Serial.println("Average sensor: " +  String(ave_temperature) + " *C");

    for (int i = 0; i < sensor_counts; i++)
    {
        // in case the conneciton is broken
        if (sensors_temp[i] < -50)
        {
            Serial.println("Sensor disconnected, incubator off");
            // analogWrite(HEATER_PIN, 0);
            sensors_error = true;
        }
    }

    // if sensors  has no error, proceed to change PID value
    if (!sensors_error)
    {
        // NOTE: optional use Xth sensor as the PID_input
        // PID_input = sensors_temp[0]
        // use ave_temperature as the PID input
        PID_input = ave_temperature;
        myPID.Compute();
        analogWrite(HEATER_PIN, PID_output);
        Serial.print("Heating effort is: ");
        Serial.println(PID_output);
    }
}

void serial_condition(String serial_input)
{
    //Serial.println(serial_input);
    // trim is needed as there is blank space and line break
    serial_input.trim();

    if (serial_input == "led_on" or serial_input == "LED_on")
    {
        // turn off the incubator to prevent current spike
        analogWrite(HEATER_PIN, 0);
        LED_colour(r, g, b);
        Serial.println("lights on");
    }
    else if (serial_input == "led_off" or serial_input == "LED_off")
    {
        LED_colour(0, 0, 0);
        Serial.println("lights off");
    }
    // move=600
    // positive is toward the camera, negative is toward the endstop
    else if (serial_input.substring(0, 4) == "move")
    {
        int distance = serial_input.substring(5).toFloat();
        Serial.print("Move by: ");
        Serial.println(distance);
        // in python, using this line to start sleep
        Serial.println("Moving the motor, stop accepting commands");
        move_stage(distance, speed);
        // this sentence indicated the motor has finished movement
        Serial.println("Finished the movement");
    }

    // set_pos=1000
    else if (serial_input.substring(0, 7) == "set_pos")
    {
        absolute_pos = serial_input.substring(8).toInt();
        Serial.print("Manually set absolute position: ");
        Serial.println(absolute_pos);
        
    }

    // speed=500
    else if (serial_input.substring(0, 5) == "speed")
    {
        Serial.print("Changing the speed to: ");
        Serial.println(serial_input.substring(6).toFloat());
        speed = serial_input.substring(6).toFloat();
        if (speed == 0)
        {
            speed = 250;
        }
        optics_stepper.setSpeed(speed);
    }

    else if (serial_input == "pos")
    {
        Serial.print("Absolute position: ");
        Serial.println(absolute_pos);
    }

    else if (serial_input == "stop")
    {
        optics_stepper.setSpeed(250);
        optics_stepper.step(0);
    }

    else if (serial_input == "home")
    {
        Serial.println("Homing ...");
        // in python, using this line to start sleep
        Serial.println("Moving the motor, stop accepting commands");
        home_stage();
        // this sentence indicated the motor has finished movement
        Serial.println("Finished the movement");
    }

    // LED_RGB=255,255,255
    else if (serial_input.substring(0, 7) == "LED_RGB" or serial_input.substring(0, 7) == "LED_rgb")
    {
        serial_input = serial_input.substring(8);
        r = (getValue(serial_input, ',', 0).toInt());
        g = (getValue(serial_input, ',', 1).toInt()); // turn the LED on (HIGH is the voltage level
        b = (getValue(serial_input, ',', 2).toInt()); // turn the LED on (HIGH is the voltage level
        LED_colour(r, g, b);
    }

    // temp=37
    else if (serial_input.substring(0, 4) == "temp")
    {
        PID_setpoint = serial_input.substring(5).toFloat();
        if (PID_setpoint > 50)
        {
            Serial.println("Maximum temperature is 50 C");
            PID_setpoint = 50;
        }
        Serial.print("Temperature is set to ");
        Serial.print(PID_setpoint);
        Serial.println(" C");
    }
}

void LED_colour(int r, int g, int b)
{
    for (int i = 0; i < NUMPIXELS; i++)
    {
        // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
        LED.setPixelColor(i, LED.Color(r, g, b)); // Moderately bright green color.
        LED.show();                               // This sends the updated pixel color to the hardware.
        delay(5);
    }
}

void move_stage(float distance, float speed)
{
    // turn off the incubator to prevent current spike
    analogWrite(HEATER_PIN, 0);
    // DEBUG: the endstop was not connected, remove comment later
    //if (distance < 0 && digitalRead(END_STOP_PIN) == LOW)
   if (distance < 0 && digitalRead(END_STOP_PIN) == HIGH)
    {
        // if hit end_stop, and still trying to move upward
        Serial.println("already at the end stop");
        absolute_pos = 0;
    }
    else
    {
        optics_stepper.setSpeed(speed);
        optics_stepper.step(distance);
        absolute_pos = absolute_pos + distance;
    }
    Serial.print("Absolute position: ");
    Serial.println(absolute_pos);
}

void home_stage()
{
    while (digitalRead(END_STOP_PIN) == HIGH)
    {
        // home at a defined speed?
        move_stage(-500, 1000);
    }
    Serial.println("Stage homed, reset the absolute position");
    // after hitting the end_stop, reset the absolute position
    move_stage(0, speed); //default position
    absolute_pos = 0;
    Serial.print("Absolute position: ");
    Serial.println(absolute_pos);
}

// sammy's home made code
String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = {0, -1};
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++)
    {
        if (data.charAt(i) == separator || i == maxIndex)
        {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i + 1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
