#!/usr/bin/env python
from importlib import import_module
import os
import time
import sys
import threading

from flask import Flask, render_template, Response, redirect, request

from serial_communication import serial_controller_class

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera


app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    Camera.start_stream()
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        # the obtained frame is a jpeg
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


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

# auto-refresh to update the config
@app.route('/c')
@app.route('/config')
def read_config():
    Camera.update_camera_setting()
    return render_template('index.html', refresh_interval=2)


@app.route('/zoom')
def zoom():
    """ Zoom in the streaming window """
    return render_template('index.html', stream_class = 'stream_zoom')

def swap_stream_method(option='swap'):
    # DEBUG: why do I need the global Camera?
    # global Camera
    if option == 'swap':
        Camera.stop_stream()
        if Camera.stream_type == 'pi':
            from camera_pi_cv import Camera
        elif Camera.stream_type == 'opencv':
            from camera_pi import Camera
        Camera.start_stream()

    elif option == 'opencv':
        if Camera.stream_type == 'pi':
            Camera.stop_stream()
            from camera_pi_cv import Camera
            Camera.start_stream()
    
    elif option == 'pi':
        if Camera.stream_type == 'opencv':
            Camera.stop_stream()
            from camera_pi import Camera
            Camera.start_stream()


    # is this necessary?
    # time.sleep(2)
    

@app.route('/swap_stream')
def swap_stream():
    ''' swap between opencv and picamera for streaming'''
    # DEBUG: why do I need the global Camera?
    # global Camera
    # Camera.stop_stream()
    # if Camera.stream_type == 'pi':
    #     from camera_pi_cv import Camera
    # elif Camera.stream_type == 'opencv':
    #     from camera_pi import Camera
    # Camera.start_stream()
    # time.sleep(2)
    swap_stream_method()
    return redirect('/')


def connect_serial():
    # initialise the serial port if it does not exist yet.
    try:
        Camera.serial_controller
    except AttributeError:
        Camera.serial_controller = serial_controller_class()
        # Change: based on the arduino name
        Camera.serial_controller.serial_connect(port_names=['SERIAL'], baudrate=9600)
        Camera.serial_controller.serial_read_threading()

@app.route('/serial/')
@app.route('/ser/')
def send_serial():
    connect_serial()
    # split the command into two parts for type (LED_RGB) and value (r,g,b)
    # the type is obtined from the dropdown
    serial_command_type = request.args.get('type', '')
    # the value is obtained from the input_form
    serial_command_value = request.args.get('s', '')

    serial_command = serial_command_type +  serial_command_value 
    Camera.serial_controller.serial_write(serial_command, parser='waterscope')
    # start a thread
    return render_template('index.html', 
        serial_command_type = serial_command_type, 
        serial_command_value=serial_command_value)


@app.route('/autofocus')
@app.route('/af')
def auto_focus():
    # swap to opencv and then start the auto focusing

    connect_serial()
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
    connect_serial()
    # default time lapse interval is 10 sec
    # to use different value - http://10.0.0.1:5000:5000/timelapse/?t=2
    refresh_interval = request.args.get('t', '10')
    Camera.serial_controller.serial_write('led_off', parser='waterscope')
    # stablise the LED before taking images
    time.sleep(1)
    Camera.take_image()
    time.sleep(1)
    Camera.serial_controller.serial_write('led_on', parser='waterscope')

    # start a thread
    return render_template('index.html', refresh_interval=refresh_interval)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)


