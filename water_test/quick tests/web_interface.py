import io
import time
import picamera
import logging
import socketserver
from threading import Condition
from http import server

from read_config import initialise_config


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    #Handler for the GET requests
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers() 
            self.wfile.write(content)
        elif self.path == '/stream':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    # Send the html message
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    # Send the html message
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True




# https://picamera.readthedocs.io/en/release-1.12/fov.html

PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream" width="1640" height="1232" />
</body>
</html>
"""


with picamera.PiCamera() as camera:
    # consistent imaging condition
    config = initialise_config()
    config.read_config_file()

    camera.resolution = (1640, 1232)
    camera.framerate = 24
    camera.awb_mode = config.awb_mode
    camera.awb_gains = config.awb_gains
    camera.iso = config.iso
    camera.shutter_speed = config.shutter_speed
    camera.saturation = config.saturation


    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    
    
    try:
        address = ('', 5000)
        #Create a web server and define the handler to manage the
	    #incoming request
        server = StreamingServer(address, StreamingHandler)
        #Wait forever for incoming htto requests
        server.serve_forever()
    finally:
        camera.stop_recording()


