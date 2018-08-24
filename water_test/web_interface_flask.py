# import required modules
from flask import Flask, render_template, Response 
import picamera 
import cv2
import socket 
import io 
from threading import Condition
app = Flask(__name__) 
vc = cv2.VideoCapture(0) 


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


# The / route serves the main page, which is defined in the index.html
@app.route('/') 
def index(): 
   """Video streaming .""" 
   return render_template('index.html') 
def gen(): 
   """Video streaming generator function.""" 
   while True: 
       rval, frame = vc.read() 
       cv2.imwrite('pic.jpg', frame) 
       yield (b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n') 

        with output.condition:
            output.condition.wait()
            frame = output.frame
            yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            b'Content-Length: {}'.format(len(frame))
            + open('pic.jpg', 'rb').read() + b'\r\n') 

        self.wfile.write(b'--FRAME\r\n')
        self.send_header('Content-Type', 'image/jpeg')
        self.send_header('Content-Length', len(frame))
        self.end_headers()
        self.wfile.write(frame)
        self.wfile.write(b'\r\n')

# The /video_feed route returns the streaming response. 
# Because this stream returns the images that are to be displayed in the web page, 
# the URL to this route is in the src attribute of the image tag.

@app.route('/video_feed') 
def video_feed(): 
   """Video streaming route. Put this in the src attribute of an img tag.""" 
   return Response(gen(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame') 


if __name__ == '__main__': 
    with picamera.PiCamera() as camera:
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')
        app.run(host='0.0.0.0', debug=True, threaded=True) 