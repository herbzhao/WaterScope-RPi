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

if len(sys.argv) > 1:
    if sys.argv[1] == 'opencv':
        from camera_pi_cv import Camera

else:
    from camera_pi import Camera


''' usage:
in browser - type

to start preview 
10.0.0.1:5000  

to take a image
10.0.0.1:5000/s

to update the config
10.0.0.1:5000/c

to take timelapse (default 10 sec time interval)
10.0.0.1:5000/tl

to take timelapse with defined time interval
10.0.0.1:5000/tl/?t=5

to send serial command
10.0.0.1:5000/serial/?s=66

'''

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


@app.route('/swap_stream')
def swap_stream():
    ''' swap between opencv and picamera for streaming'''
    global Camera
    Camera.stop_stream()
    if Camera.stream_type == 'pi':
        from camera_pi_cv import Camera
    elif Camera.stream_type == 'opencv':
        from camera_pi import Camera
    Camera.start_stream()
    time.sleep(2)
    return redirect('/')


@app.route('/serial/')
@app.route('/ser/')
def send_serial():
    # initialise the serial port
    try:
        Camera.serial_controller
    except AttributeError:
        #global ser
        Camera.serial_controller = serial_controller_class()
        Camera.serial_controller.serial_read_threading()

    general_serial_command = request.args.get('s', '')
    move_serial_command = request.args.get('m', '')

    Camera.serial_controller.send_arduino_command(str(general_serial_command))
    Camera.serial_controller.send_arduino_command('move {}'.format(str(move_serial_command)))
    # start a thread
    return render_template('index.html', general_serial_command = general_serial_command, move_serial_command = move_serial_command)


@app.route('/autofocus')
@app.route('/af')
def auto_focus():
    # swap to opencv and then start the auto focusing
    global Camera
    if Camera.stream_type == 'pi':
        Camera.stop_stream()
        from camera_pi_cv import Camera
        Camera.start_stream()
        time.sleep(2)

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
    # initialise the serial port
    try:
        serial_controller
    except NameError:
        #global ser
        serial_controller = serial_controller_class()
        serial_controller.serial_read_threading()

    # default time lapse interval is 10 sec
    # to use different value - http://10.0.0.1:5000:5000/timelapse/?t=2
    refresh_interval = request.args.get('t', '10')
    serial_controller.send_arduino_command('66')
    # stablise the LED before taking images
    time.sleep(1)
    Camera.take_image()
    time.sleep(1)
    serial_controller.send_arduino_command('-66')
    # start a thread
    return render_template('index.html', refresh_interval=refresh_interval)






if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)


