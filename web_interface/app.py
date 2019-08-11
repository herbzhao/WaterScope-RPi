#!/usr/bin/env python
from importlib import import_module
import time
import datetime

from flask import Flask, render_template, Response, redirect, request, jsonify
import yaml
import numpy as np
import threading

from serial_communication import serial_controller_class, Arduinos

# a module to set system time of RaspberryPi time
from set_time import set_pi_time

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera
Camera.stream_method = 'PiCamera'

app = Flask(__name__)


def gen(camera):
    """Video streaming generator function."""
    while True:
        # the obtained frame is a jpeg
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



def initialise_serial_connection():
    ''' all the arduino connection is done via this function''' 
    try:
        # print(' serial connections already exist')
        Arduinos.serial_controllers
    except AttributeError:
        with open('config_serial.yaml') as config_serial_file:
            serial_controllers_config = yaml.load(config_serial_file)
        Arduinos.available_arduino_boards = []

        for board_name in serial_controllers_config:
            if serial_controllers_config[board_name]['connect'] is True:
                Arduinos.available_arduino_boards.append(board_name)

        print(Arduinos.available_arduino_boards)
        # initialise the serial port if it does not exist yet.
        #print('initialising the serial connections')
        Arduinos.serial_controllers = {}
        for name in Arduinos.available_arduino_boards:
            Arduinos.serial_controllers[name] = serial_controller_class()
            Arduinos.serial_controllers[name].serial_connect(
                port_address=serial_controllers_config[name]['port_address'],
                port_names=serial_controllers_config[name]['port_names'], 
                baudrate=serial_controllers_config[name]['baudrate'])
            Arduinos.serial_controllers[name].serial_read_threading(
                options=serial_controllers_config[name]['serial_read_options'], 
                parsers=serial_controllers_config[name]['serial_read_parsers'])

def parse_serial_time_temp():
    # synchronise the arduino_time
    initialise_serial_connection()
    try:
        time_value = Arduinos.serial_controllers['waterscope'].log['time'][-1]
        temp_value = Arduinos.serial_controllers['waterscope'].log['temp'][-1]

    except (IndexError, KeyError, AttributeError): 
        time_value = 0
        temp_value = 0

    minute, second = divmod(time_value,60)
    hour, minute = divmod(minute, 60)
    time_value_formatted = datetime.time(int(hour), int(minute), int(second))
    # use a arbitrary date for plotly to work properly
    time_value_formatted = datetime.datetime.combine(datetime.date(1, 1, 1), time_value_formatted)

    return time_value_formatted, temp_value

@app.route('/')
def index():
    """Video streaming home page."""
    Camera.start_stream()
    initialise_serial_connection()
    return render_template('index.html')


@app.route('/v')
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/update_time/')
def update_time():
    user_time = request.args.get('user_time', '')
    set_pi_time(user_time)
    print('system time has been updated')

    return jsonify({"user_time": user_time})



# DEBUG: combine the info with this page?
@app.route('/settings/')
def settings_io():
    ''' swap between opencv and picamera for streaming'''
    # set default value for the stream_method
    try:
        Camera.stream_method
    except AttributeError:
        Camera.stream_method = 'PiCamera'

    zoom_value = request.args.get('zoom_value', '')
    config_update = request.args.get('config_update', '')
    stop_flag = request.args.get('stop', '')

    if zoom_value is not '':
        # only change zoom when passing an arg
        Camera.change_zoom(zoom_value)
    if config_update == 'true':
        Camera.update_camera_setting()
    if stop_flag == 'true':
        Camera.stop_stream()

    with open('config_picamera.yaml') as config_file:
        config = yaml.load(config_file)
        default_LED_RGB = config['default_LED_RGB']
        print(default_LED_RGB)

    settings = {
        'stream_method': Camera.stream_method, 
        'available_arduino_boards': Arduinos.available_arduino_boards,
        'default_LED_RGB': default_LED_RGB
        }

    return jsonify(settings)


@app.route('/change_stream_method/')
def change_stream_method(option=''):
    # DEBUG: why do I need the global Camera?
    global Camera
    # when not specify option, use the request
    if option is '':
        new_stream_method = request.args.get('stream_method', 'PiCamera')
        option = new_stream_method

    if option == 'OpenCV':
        print('Change the stream method to OpenCV')
        # only change the stream method if the current one is not right
        if Camera.stream_method == 'PiCamera':
            Camera.stop_stream()
            from camera_pi_cv import Camera
            Camera.stream_method = 'OpenCV'
            Camera.start_stream()
            time.sleep(0.1)
    
    elif option == 'PiCamera':
        print('Change the stream method to Picamera')
        # only change the stream method if the current one is not right
        if Camera.stream_method == 'OpenCV':
            Camera.stop_stream()
            from camera_pi import Camera
            Camera.stream_method = 'PiCamera'
            Camera.start_stream()
            time.sleep(0.1)



# DEBUG: join the serial window and serial send 
''' general serial command url'''
@app.route('/send_serial/')
def send_serial():
    initialise_serial_connection()
    # choose the arduino board and parser - ferg, waterscope, para
    serial_board = request.args.get('board', 'waterscope')
    # the value is obtained from the input_form
    serial_command_value = request.args.get('value', '')

    try:
        Arduinos.serial_controllers[serial_board].serial_write(serial_command_value, parser=serial_board)
    except KeyError:
        print('cannot find this board')
    
    return render_template('serial_window.html')


''' The feed for serial_command output ''' 
@app.route('/serial_time_temp')
def serial_time_temp():
    time_value_formatted, temp_value = parse_serial_time_temp()
    now = datetime.datetime.now()
    time_value_formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    date = now.date()
    second = now.second
    minute = now.minute
    hour = now.hour
    # return jsonify({'time_value':time_value, 'temp_value':temp_value})
    return jsonify({'x':time_value_formatted, 'date': str(date), 'hour':hour, 'minute': minute, 'second': second, 'y':temp_value})

''' Used to identify whether motor is busy ''' 
@app.route('/waterscope_motor_status')
def check_waterscope_motor_status():
    # stop sending command when motor is busy
    # initialise_serial_connection()
    stepper_optics_busy = Arduinos.serial_controllers['waterscope'].stepper_optics_busy
    absolute_z = Arduinos.serial_controllers['waterscope'].absolute_z
    # # NOTE: initilaise the motor_idle to be true
    return jsonify({'stepper_optics_busy':stepper_optics_busy, 'absolute_z': absolute_z})
    # return jsonify({'stepper_optics_busy': False, 'absolute_z': 0})
    


@app.route('/auto_focus/')
def auto_focus():
    # swap to opencv and then start the auto focusing
    # NOTE: Do we need to use the URL rather than calling the function directly
    command = request.args.get('command', '')
    try:
        Camera.auto_focus_status
    except AttributeError:
        Camera.auto_focus_status = 'Waiting for auto focusing'

    if command == 'start':
        change_stream_method(option='OpenCV')
        initialise_serial_connection()
        # start auto focusing
        Camera.start_auto_focus_thread()
        Camera.auto_focus_status = 'auto focusing...'
        return render_template('index.html') 
    elif command == 'done':
        Camera.auto_focus_status = 'auto focus completed'
        return render_template('index.html')
    else:
        return jsonify({'auto_focus_status': Camera.auto_focus_status})



# input filename and filename options and method
def parse_filename_and_acquire_data(filename, method):
    # the filename is consist of user defined value and the time stamp
    # arduino_time is the seconds from the booting up 
    # raspberry_time is the absolute time
    # synchronise the arduino_time
    if 'arduino_time' in filename:
        # HH:MM:SS format
        time_value_formatted, temp_value = parse_serial_time_temp()
        # allowing other appendix
        filename = str(time_value_formatted.time()) + '_T{}'.format(temp_value) + filename.replace('arduino_time', '')
    # synchronise the raspberry pi time
    # to set pi's time: sudo date -s '2017-02-05 15:30:00'
    elif 'raspberry_pi_time' in filename:
        time_value_formatted, temp_value = parse_serial_time_temp()
        # DEBUG: alfred says this is a problem
        now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # allowing other appendix
    filename = now + '_T{}'.format(temp_value) + filename.replace('raspberry_pi_time', '')

    if method == 'normal':
        Camera.take_image(resolution='normal', filename=filename)
    elif method == 'high_res':
        Camera.take_image(resolution='high_res', filename=filename)
    elif method == 'waterscope':
        # waterscope method requires LED to be only on when taking images
        Arduinos.serial_controllers['waterscope'].serial_write('led_on', parser='waterscope')
        time.sleep(2)
        Camera.take_image(resolution='high_res', filename=filename)
        time.sleep(2)
        Arduinos.serial_controllers['waterscope'].serial_write('led_off', parser='waterscope')

# a function to take timelapse depending on the method
def take_timelapse(timelapse_interval=10, method='normal'):
    while True:
        parse_filename_and_acquire_data('raspberry_pi_time', method)
        time.sleep(timelapse_interval)
        # a flag that determines whether to stop timelapse
        if Camera.stop_timelapse == True:
            break
            
# take one image
@app.route('/acquire_data/')
def acquire_data():
    # the filename is consist of user defined value and the time stamp           
    filename = request.args.get('filename', '')

    # the option determines whether it is the video recording, high_resolution image, or timelapse
    option = request.args.get('option', '')
    # Note: args: image capture - option='normal' or 'high_res'
    if option == '' or option == 'normal':
        parse_filename_and_acquire_data(filename, 'normal')
    elif option == 'high_res':
        parse_filename_and_acquire_data(filename, 'high_res')

    elif 'timelapse_' in option:
        # this method allows the timelapse to be taken when the browser is closed, but the terminal needs to be open
        # NOTE: args: high_res_timelapse_10, normal_timelapse_10, waterscope_timelapse_10
        # parse the timelapse_interval and method from the option arg 
        print(option)
        timelapse_interval = int(option.split('timelapse_')[1])
        # the method "waterscope" or "normal" is string before _timelapse
        method = option.split('_timelapse_')[0]

        # NOTE: a flag that help to terminate the threading later
        Camera.stop_timelapse = False
        timelapse_thread = threading.Thread(target=take_timelapse, args=[timelapse_interval, method])
        # DEBUG: Check whether the daemon is needed
        timelapse_thread.daemon = True
        timelapse_thread.start()
    
    elif option == 'stop_timelapse':
        # a flag that will terminate all the timelapse
        Camera.stop_timelapse = True

    # video capture
    elif option == 'start_recording_video':
        Camera.video_recording_thread(filename=filename, recording_flag=True)
    elif option == 'stop_recording_video':
        Camera.video_recording_thread(recording_flag=False)

    return render_template('index.html')





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)