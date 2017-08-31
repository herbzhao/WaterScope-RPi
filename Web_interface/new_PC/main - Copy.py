from flask import Flask, render_template, request, jsonify, Response
import json
import sys
import time
import subprocess


# cutomised modules
from test_module import test_modules

app = Flask(__name__)


# MJPEG streaming library
class MJpegStream():
    def __init__(self):
        self.proc = None
        self.params = MultiDict()

    def start(self, params):
        """
        Start mjpg-streamer, wait until it has warmed up, and return success/failure
        """
        if self.proc:
            self.stop()
        self.proc = subprocess.Popen(self.create_args(params),
                                     stderr=subprocess.PIPE, universal_newlines=True)

        # Block until we have read the line "Encoder Buffer Size" from stderr.
        while self.proc.poll() is None:
            time.sleep(0.01)
            line = self.proc.stderr.readline()
            if line != "":
                sys.stdout.write(line)
                sys.stdout.flush()
                if "Encoder Buffer Size" in line:
                    print("mjpg-streamer successfully started!")
                    # Save our parameters if the stream starts ok
                    self.params = params
                    return True

        # If mjpg-streamer stopped, it means there was an error.
        sys.stdout.write(self.proc.stderr.read())
        sys.stderr.write("Error starting mjpg-streamer!\n")
        self.proc = None
        return False

    def stop(self):
        """
        Kill mjpg-streamer, wait until it has stopped, then return.
        """
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
        self.proc = None

    def create_args(self, params):
        return ['mjpg_streamer', '-o', 'output_http.so -w ./www', '-i', 
                'input_raspicam.so -x {0} -y {1} -fps {2} -sh {3} -co {4} -br {5} -sa {6}'
                    .format(params['width'],
                            params['height'],
                            params['fps'], 
                            params['sharpness'], 
                            params['contrast'], 
                            params['brightness'], 
                            params['saturation'])]

    def safe_args(self, params=MultiDict()):
        width = params.get('width', type=int)
        height = params.get('height', type=int)
        fps = params.get('fps', type=int)
        sharpness = params.get('sharpness', type=int)
        contrast = params.get('contrast', type=int)
        brightness = params.get('brightness', type=int)
        saturation = params.get('saturation', type=int)

        # Do some error checking for security, as we pass those values on to mjpg_streamer.
        supported_resolutions = [(1280, 720),
                                  (1920, 1080),
                                  (640, 480),
                                  (320, 240)]
        if (width, height) not in supported_resolutions:
            width, height = (self.params.get('width', 1280),
                             self.params.get('height', 720))
        supported_fps = range(1, 31)
        if fps not in supported_fps:
            fps = self.params.get('fps', 10)
        if sharpness not in range(-100,101):
            sharpness = self.params.get('fps', 0)
        if contrast not in range(-100,101):
            contrast = self.params.get('contrast', 0)
        if brightness not in range(0,101):
            brightness = self.params.get('brightness', 50)
        if saturation not in range(-100,101):
            saturation = self.params.get('saturation', 0)

        return MultiDict({
            "width": width,
            "height": height,
            "fps": fps,
            "sharpness": sharpness,
            "contrast": contrast,
            "brightness": brightness,
            "saturation": saturation,
        })

# run the library when starting
stream = MJpegStream()
# Try to start mjpg-streamer right now, but don't crash if it fails.
try:
    stream.start(params=stream.safe_args())
except Exception:
    pass









@app.route('/')
def index():
    return render_template('index.html')


@app.route("/time_lapse_module", methods=['POST','GET'])
def test():
    testing_module = test_modules()
    testing_module.time_lapse_write_file()
    return render_template('index.html');


@app.route("/update_parameters", methods=['POST','GET'])
def test2():
    # obtain JSON file sent from post or get
    parameters = request.get_json()
    print(parameters)
    testing_module = test_modules()
    testing_module.update_file_with_argument(parameters['Brightness'], parameters['Contrast'])

    return render_template('index.html');


@app.route("/read_parameters", methods=['POST','GET'])
def test3():
    testing_module = test_modules()
    parameters = testing_module.read_config_file()
    #brightness = par ameters['brightness']
    #contrast = parameters['contrast']
    # Response is more general than jsonify
    return Response(json.dumps(parameters));






@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/start_stream', methods=['GET'])
def start_stream():
    """
    Restarts the mjpg-streamer stream, waits to see if it has completed
    properly, and returns success/error.
    """
    get_args = stream.safe_args(request.args)
    if stream.start(get_args):
        return Response(status="200 OK")
    else:
        return Response(status="500 INTERNAL SERVER ERROR")

@app.route('/capture', methods=['GET'])
def capture():
    """
    Capture a still photo at max resolution and save it at static/capture.jpg
    """

    # Need to stop the stream first
    stream.stop()

    get_args = stream.safe_args(request.args)

    raspistill_args = ['raspistill', '--width', '2592', '--height', '1944',
                       '--nopreview', '--output', 'static/capture.jpg', '--timeout', '1500',
                       '--quality', '100', '--thumb', 'none',
                       '-sh', str(get_args['sharpness']), '-co', str(get_args['contrast']),
                       '-br', str(get_args['brightness']), '-sa', str(get_args['saturation'])]
    raspistill_proc = subprocess.Popen(raspistill_args)
    raspistill_proc.wait()

    # Start the stream again, with the previous parameters implied
    stream_args = stream.safe_args()
    stream.start(stream_args)

    if raspistill_proc.returncode == 0:
        return Response(status="200 OK")
    else:
        return Response(status="500 INTERNAL SERVER ERROR")





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)