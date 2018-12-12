#!/usr/bin/env python
from importlib import import_module
import time
import datetime

from flask import Flask, render_template, Response, redirect, request, jsonify
import yaml
import numpy as np

from serial_communication import serial_controller_class, Arduinos

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



def initialse_serial_connection():
    ''' all the arduino connection is done via this function''' 
    try:
        # print(' serial connections already exist')
        Arduinos.serial_controllers
    except AttributeError:
        print('''
        
        
        Connecting serial connection
        
        
        ''')
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
                port_names=serial_controllers_config[name]['port_names'], 
                baudrate=serial_controllers_config[name]['baudrate'])
            Arduinos.serial_controllers[name].serial_read_threading(options=serial_controllers_config[name]['serial_read_options'])

def parse_serial_time_temp():
    # synchronise the arduino_time
    initialse_serial_connection()
    try:
        time_value = Arduinos.serial_controllers['waterscope'].log['time'][-1]
        temp_value = Arduinos.serial_controllers['waterscope'].log['temp'][-1]
        print('temp: {}'.format(temp_value) )

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
    initialse_serial_connection()
    return render_template('index.html')


@app.route('/v')
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')




# DEBUG: combine the info with this page?
@app.route('/settings/')
def settings_io():
    ''' swap between opencv and picamera for streaming'''
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

    settings = {
        'stream_method': Camera.stream_method, 
        'available_arduino_boards': Arduinos.available_arduino_boards,
        }

    return jsonify(settings)


@app.route('/change_stream_method/')
def change_stream_method(option='OpenCV'):
    # DEBUG: why do I need the global Camera?
    global Camera
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
@app.route('/serial/')
@app.route('/ser/')
def send_serial():
    initialse_serial_connection()
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



# TODO: have a fine focus and coarse focus
@app.route('/autofocus')
@app.route('/af')
def auto_focus():
    # swap to opencv and then start the auto focusing
    change_stream_method(option='OpenCV')
    initialse_serial_connection()
    # start auto focusing
    Camera.auto_focus_thread()
    return render_template('index.html')

# take one image
@app.route('/take_image/')
def take_image():
    option = request.args.get('option')
    filename= request.args.get('filename', '')
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
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # allowing other appendix
        filename = now + '_T{}'.format(temp_value) + filename.replace('raspberry_pi_time', '')
        
    # video capture
    if option == 'start_recording':
        Camera.video_recording_thread(filename=filename, recording_flag=True)
    elif option == 'stop_recording':
        Camera.video_recording_thread(recording_flag=False)
    # image capture
    elif option == 'high_res':
        Camera.take_image(resolution='high_res', filename=filename)
    # waterscope_timelapse_nohup_100
    elif 'waterscope_timelapse_nohup' in option:
        # Camera.stop_stream()
        timelapse_interval = int(option.replace('waterscope_timelapse_nohup_', ''))
        while True:
            Arduinos.serial_controllers['waterscope'].serial_write('led_on', parser='waterscope')
            time.sleep(2)
            Camera.take_image(resolution='high_res', filename=filename)
            time.sleep(2)
            Arduinos.serial_controllers['waterscope'].serial_write('led_off', parser='waterscope')
            time.sleep(timelapse_interval)



        
    else:
            Camera.take_image(resolution='normal', filename=filename)

    # start a thread
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)