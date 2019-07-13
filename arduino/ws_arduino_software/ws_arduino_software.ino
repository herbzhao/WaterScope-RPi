#include <math.h>

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
#define HEATER_PIN 3

// LEDs
#include <Adafruit_NeoPixel.h>
#define LED_PIN 4
#define NUMPIXELS 12
Adafruit_NeoPixel LED = Adafruit_NeoPixel(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);
// starting LED colour
int r = 5, g = 5, b = 5;

//motor controls
#include <AccelStepper.h>
// https://groups.google.com/forum/#!topic/accelstepper/tIL5XN3WLVE
// AccelStepper doesn't know the steps/revolution
AccelStepper stepper_optics(AccelStepper::FULL4WIRE, 11, 13, 12, 10);
AccelStepper stepper_carousel(AccelStepper::FULL4WIRE, 7, 9, 8, 6);

// use this value to convert the um movement to steps
float stepper_optics_ratio = 0.5;
// use this value to convert the angles to steps
float stepper_carousel_ratio = 6;

#define END_STOP_PIN_OPT A0
#define END_STOP_PIN_CAR A0

int max_speed_optics = 500;
int max_speed_carousel = 500;
int speed_optics = 300;
int speed_carousel = 300;

// DEBUG: this is wrong
float absolute_pos_optics = 0;
float absolute_pos_carousel = 0;

// Threading
#include <Thread.h>
#include <ThreadController.h>
// ThreadController that will controll all threads
ThreadController thread_controller = ThreadController();
Thread read_temp_adjust_heating_thread = Thread();
Thread check_motor_status_thread = Thread();
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
    // DEBUG: disable heating temporarily
    PID_setpoint = 0; 
    myPID.SetOutputLimits(1, 255);

    // for the motor, needs to set an acceleration
    stepper_optics.setAcceleration(2000);
    stepper_carousel.setAcceleration(2000);

    // Configure Threads
    read_temp_adjust_heating_thread.onRun(read_temp_adjust_heating);
    read_temp_adjust_heating_thread.setInterval(5000);
    check_motor_status_thread.onRun(check_motor_status);
    check_motor_status_thread.setInterval(500);
    read_serial_thread.onRun(read_serial);
    read_serial_thread.setInterval(200);
    // Adds  threads to the controller
    //thread_controller.add(&read_serial_thread);
    thread_controller.add(&read_temp_adjust_heating_thread); // & to pass the pointer to it
    thread_controller.add(&check_motor_status_thread); // & to pass the pointer to it


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
    read_serial();
    // run the threads
    thread_controller.run();
    // the motor will execute whenever a command is waiting
    stepper_carousel.run();
    stepper_optics.run();
}

void read_serial(void)
{
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
    Serial.println("Average sensor: " + String(ave_temperature) + "°C");

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
    // LED_RGB=255,255,255
    else if (serial_input.substring(0, 7) == "LED_RGB" or serial_input.substring(0, 7) == "LED_rgb")
    {
        serial_input = serial_input.substring(8);
        r = (getValue(serial_input, ',', 0).toInt());
        g = (getValue(serial_input, ',', 1).toInt()); // turn the LED on (HIGH is the voltage level
        b = (getValue(serial_input, ',', 2).toInt()); // turn the LED on (HIGH is the voltage level
        LED_colour(r, g, b);
    }
    // move_opt=600
    // move_car=30 (degrees)
    // positive is toward the camera, negative is toward the endstop
    else if (serial_input.substring(0, 4) == "move")
    {
        String motor_type = serial_input.substring(5, 8);
        int distance = serial_input.substring(9).toFloat();
        move_stage(motor_type, distance);
    }

    // speed_car=500
    else if (serial_input.substring(0, 5) == "speed")
    {
        String motor_type = serial_input.substring(6, 9);
        int speed = serial_input.substring(10).toFloat();
        if (motor_type == "opt")
        {
            if (speed <= 50)
            {
                speed = 50;
            }
            else if (speed >=max_speed_optics)
            {
                speed = max_speed_optics;
            }
            
            speed_optics = speed;
            Serial.println("Changing the stepper_optics speed to: " + String(speed));
        }

        else if (motor_type == "car")
        {
            if (speed <= 50)
            {
                speed = 50;
            }
            else if (speed >=max_speed_carousel)
            {
                speed = max_speed_optics;
            }
            
            speed_carousel = speed;
            Serial.println("Changing the stepper_carousel speed to: " + String(speed));
        }
    }

    else if (serial_input == "pos")
    {
        Serial.print("Absolute optic stage position: ");
        Serial.print(absolute_pos_optics);
        Serial.println(" um");
        Serial.print("Absolute optic carousel position: ");
        Serial.print(absolute_pos_carousel);
        Serial.println("°");
    }
    
    // set_home_opt  or set_home_car
    else if (serial_input.substring(0, 8) == "set_home")
    {
        String motor_type = serial_input.substring(9);
        if (motor_type == "opt")
        {
            absolute_pos_optics = 0;
        }
        else if (motor_type == "car"){
            absolute_pos_carousel = 0;
        }
    }  
    
    else if (serial_input == "stop")
    {
        stepper_optics.stop();
        stepper_carousel.stop();
    }

    // home_opt and home_car
    else if (serial_input.substring(0, 4) == "home")
    {
        String motor_type = serial_input.substring(5, 8);
        home_stage(motor_type);
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
// a thread that runs every 500ms to check motor is busy or not
void check_motor_status(){
    Serial.print("stepper_optics: ");
    if (stepper_optics.isRunning()){
        Serial.println("busy");
    }
    else{
        Serial.println("ready");
    }
    Serial.print("stepper_carousel: ");
    if (stepper_carousel.isRunning()){
        Serial.println("busy");
    }
    else{
        Serial.println("ready");
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

void move_stage(String motor_type, float distance)
{
    // turn off the incubator to prevent current spike
    analogWrite(HEATER_PIN, 0);

    if (motor_type == "opt")
    {
        // DEBUG: the endstop was not connected, remove comment later
        //if (distance < 0 && digitalRead(END_STOP_PIN) == LOW)
        if (distance < 0 && digitalRead(END_STOP_PIN_OPT) == HIGH)
        {
            // if hit end_stop, and still trying to move towards end_stop
            Serial.println("already at the end stop");
            absolute_pos_optics = 0;
        }
        else
        {
            stepper_optics.setMaxSpeed(speed_optics);
            // in python, using this line to start sleep
            Serial.println("Moving the motor, stop accepting commands");
            // convert distance in um  to steps
            int motor_steps = distance * stepper_optics_ratio;
            stepper_optics.move(motor_steps);
            // in Python,  this sentence indicated the motor has finished movement
            Serial.println("Finished the movement");

            absolute_pos_optics = absolute_pos_optics + distance;
            Serial.println("Move by: " + String(distance) + "um");
        }
        Serial.print("Optical stage absolute position: ");
        Serial.println(absolute_pos_optics);
    }
    else if (motor_type == "car")
    {
        stepper_carousel.setMaxSpeed(speed_carousel);
        // convert degrees to steps
        int motor_steps = distance * stepper_carousel_ratio;
        // in python, using this line to start sleep
        Serial.println("Moving the motor, stop accepting commands..");

        stepper_carousel.move(motor_steps);
        stepper_carousel.run();
        // in Python,  this sentence indicated the motor has finished movement
        Serial.println("Finished the movement");
        // the range of degree - 0 to 360
        absolute_pos_carousel += distance;
        absolute_pos_carousel = fmod(absolute_pos_carousel, 360);

        Serial.println("Move by: " + String(distance) + "°");
        Serial.println("Carousel absolute position: " + String(absolute_pos_carousel) + "°");
    }
}

void home_stage(String motor_type)
{
    if (motor_type == "opt")
    {
        while (digitalRead(END_STOP_PIN_OPT) == HIGH)
        {
            move_stage("opt", -100);
        }
        // after hitting the end_stop, reset the absolute position
        absolute_pos_optics = 0;
    }
    else if (motor_type == "car")
    {
        while (digitalRead(END_STOP_PIN_CAR) == HIGH)
        {
            move_stage("car", 10);
        }
        // after hitting the end_stop, reset the absolute position
        absolute_pos_carousel = 0;
    }
    Serial.println("Stage homed, reset the absolute position");
}

// sammy's home made code to extract RGB value
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
