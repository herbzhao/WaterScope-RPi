#!/usr/bin/env python
from importlib import import_module
import os
import time
import sys
import threading

from flask import Flask, render_template, Response, redirect, request

from serial_communication import connect_serial, send_arduino_command,  serial_read_once, serial_read_continuous

# Raspberry Pi camera module (requires picamera package)
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
    return render_template('index.html')

# a help page
@app.route('/h')
@app.route('/help')
def help_page():
    return render_template('help.html', refresh_interval=2)


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


# auto-refresh to update the config
@app.route('/c')
@app.route('/config')
def read_config():
    Camera.update_camera_setting()
    return render_template('index.html', refresh_interval=2)


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
@app.route('/serial/')
@app.route('/ser/')
def send_serial():
    try:
        ser
    except NameError:
        ser = connect_serial()
        # somehow need to read once for the arduino to work
        # serial_read_once(ser)
        # if you want to read serial continously
        threading1 = threading.Thread(target=serial_read_continuous, args=[ser])
        threading1.daemon = True
        threading1.start()

    general_serial_command = request.args.get('s', '')
    move_serial_command = request.args.get('m', '')

    send_arduino_command(ser, str(general_serial_command))
    send_arduino_command(ser, 'move {}'.format(str(move_serial_command)))
    print(general_serial_command)
    print(move_serial_command)
    # start a thread
    return render_template('index.html', general_serial_command = general_serial_command, move_serial_command = move_serial_command)



if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)


