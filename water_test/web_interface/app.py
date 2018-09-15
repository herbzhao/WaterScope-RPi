#!/usr/bin/env python
from importlib import import_module
import os
import time
from threading import Timer

from flask import Flask, render_template, Response, redirect, request

# import camera driver
# if os.environ.get('CAMERA'):
#     Camera = import_module('camera_' + os.environ['CAMERA']).Camera
# else:
#     from camera import Camera

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera




app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html', time_int=30)


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


''' usage:
in browser - type

to start preview 
10.0.0.1  

to take a image
10.0.0.1/s

to take timelapse (default 10 sec time interval)
10.0.0.1/tl

to take timelapse with defined time interval
10.0.0.1/tl/?t=5

'''

# auto-refresh to update the config
@app.route('/config')
def read_config():
    Camera.read_camera_setting()
    return render_template('index.html', time_int=2)

# take one image
@app.route('/snap')
@app.route('/s')
def take_image():
    Camera.take_image()
    # start a thread
    return render_template('index.html', time_int=9999)

# this template includes an auto-refresh to keep snapping :D
@app.route('/timelapse/')
@app.route('/tl/')
def take_timelapse():
    # default time lapse interval is 10 sec
    # to use different value - http://10.0.0.1:5000/timelapse/?t=2
    time_int = request.args.get('t', 10)
    Camera.take_image()
    # start a thread
    return render_template('index.html', time_int=time_int)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
