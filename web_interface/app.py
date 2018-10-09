#!/usr/bin/env python
from importlib import import_module
import time

from flask import Flask, render_template, Response, redirect, request, jsonify
import yaml
import numpy as np

from serial_communication import serial_controller_class

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera

# TEST: just temporary
from output import output_class_builder 


app = Flask(__name__)




def gen(camera):
    """Video streaming generator function."""
    while True:
        # the obtained frame is a jpeg
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def swap_stream_method(option='swap'):
    # DEBUG: why do I need the global Camera?
    global Camera
    if option == 'swap':
        Camera.stop_stream()
        if Camera.stream_type == 'pi' or Camera.stream_type =='PiCamera':
            from camera_pi_cv import Camera
        elif Camera.stream_type == 'opencv' :
            from camera_pi import Camera
        Camera.start_stream()
        time.sleep(0.1)

    elif 'cv' in option or  'CV' in option:
        if Camera.stream_type == 'pi':
            Camera.stop_stream()
            from camera_pi_cv import Camera
            Camera.start_stream()
            time.sleep(0.1)
    
    elif 'pi' in option or 'Pi' in option:
        if Camera.stream_type == 'opencv':
            Camera.stop_stream()
            from camera_pi import Camera
            Camera.start_stream()
            time.sleep(0.1)


def initialse_serial_connection():
    ''' all the arduino connection is done via this function''' 
    try:
        #print(' serial connections already exist')
        Camera.serial_controllers
    except AttributeError:
        with open('config_serial.yaml') as config_serial_file:
            serial_controllers_config = yaml.load(config_serial_file)
        # Warning: depends on what boards are connected
        serial_controllers_names = ['ferg','parabolic']
        # initialise the serial port if it does not exist yet.
        #print('initialising the serial connections')
        Camera.serial_controllers = {}
        for name in serial_controllers_names:
            Camera.serial_controllers[name] = serial_controller_class()
            Camera.serial_controllers[name].serial_connect(
                port_names=serial_controllers_config[name]['port_names'], 
                baudrate=serial_controllers_config[name]['baudrate'])
            Camera.serial_controllers[name].serial_read_threading(options=serial_controllers_config[name]['serial_read_options'])


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


@app.route('/stop')
def stop():
    """Stop the camera."""
    Camera.stop_stream()
    return render_template('index.html')


@app.route('/zoom')
def zoom():
    """ Zoom in the streaming window """
    return render_template('index.html', stream_class = 'stream_zoom')


# auto-refresh to update the config
@app.route('/c')
@app.route('/config')
def read_config():
    Camera.update_camera_setting()
    return render_template('index.html', refresh_interval=1)

@app.route('/swap_stream/')
def swap_stream():
    ''' swap between opencv and picamera for streaming'''
    stream_method = request.args.get('stream', '')
    swap_stream_method(option=stream_method)

    return redirect('/')

@app.route('/info')
def info():
    # a page to send all the current info to vue
    return jsonify({'stream_method': Camera.stream_type})

''' general serial command url'''
@app.route('/serial/')
@app.route('/ser/')
def send_serial():
    initialse_serial_connection()
    # choose the arduino board and parser - ferg, waterscope, para
    serial_board = request.args.get('board', 'parabolic')
    # split the command into two parts for type (LED_RGB) and value (r,g,b)
    # the type is obtined from the dropdown
    serial_command_type = request.args.get('type', '')
    # the value is obtained from the input_form
    serial_command_value = request.args.get('value', '')
    # TODO: test the serial command and then simplify the template
    serial_command = serial_command_type +  serial_command_value +')'
    print(serial_command)
    try:
        Camera.serial_controllers[serial_board].serial_write(serial_command, parser = serial_board)
    except KeyError:
        print('cannot find this board')
    
    return render_template('index.html', 
        serial_board = serial_board, 
        serial_command_type = serial_command_type, 
        serial_command_value=serial_command_value)


''' The feed for serial_command output ''' 
@app.route('/parabolic_serial_monitor')
def parabolic_serial_monitor():
    initialse_serial_connection()
    try:
        time_value = Camera.serial_controllers['parabolic'].log['time'][-1]
        temp_value = Camera.serial_controllers['parabolic'].log['temp'][-1]
    except IndexError:
        time_value = 0
        temp_value = 0
    # return jsonify({'time_value':time_value, 'temp_value':temp_value})
    return jsonify({'x':time_value, 'y':temp_value})



# TODO: have a fine focus and coarse focus
@app.route('/autofocus')
@app.route('/af')
def auto_focus():
    # swap to opencv and then start the auto focusing
    swap_stream_method(option='opencv')
    initialse_serial_connection()
    # start auto focusing
    Camera.auto_focus_thread()
    return render_template('index.html')

# take one image
@app.route('/snap')
@app.route('/s')
def take_image():
    Camera.take_image()
    # start a thread
    return render_template('index.html')


# this template includes an auto-refresh to keep snapping :D
@app.route('/timelapse/')
@app.route('/tl/')
def take_timelapse():
    # default time lapse interval is 10 sec
    # to use different value - http://10.0.0.1:5000:5000/timelapse/?t=2
    refresh_interval = request.args.get('t', '')
    Camera.take_image()
    # start a thread
    return render_template('index.html', refresh_interval=refresh_interval)


# this template includes an auto-refresh to keep snapping :D
@app.route('/timelapse_waterscope/')
@app.route('/tl_ws/')
def take_timelapse_waterscope():
    # default time lapse interval is 10 sec
    # to use different value - http://10.0.0.1:5000:5000/timelapse/?t=2
    refresh_interval = request.args.get('t', '10')
    initialse_serial_connection()
    Camera.serial_controllers['waterscope'].serial_write('led_off', parser='waterscope')
    # stablise the LED before taking images
    time.sleep(1)
    Camera.take_image()
    time.sleep(1)
    Camera.serial_controllers['waterscope'].serial_write('led_on', parser='waterscope')

    # start a thread
    return render_template('index.html', refresh_interval=refresh_interval)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)