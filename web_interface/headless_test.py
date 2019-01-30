import requests
import time
import threading

''' this allows us to start autofocus and timelapse without using the browser'''

base_URL = "http://localhost:5000" 
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}



def activate_camera_module():
    ''' activate video feed is necessary to run the camera ''' 
    video_URL = base_URL + '/v'
    print('start camera')
    video_URL_requests = requests.get(video_URL, headers = headers)

def activate_camera_module_thread():
    threading_video_feed = threading.Thread(target=activate_camera_module)
    threading_video_feed.daemon = True
    threading_video_feed.start()
    time.sleep(5)


print('starting the camera')
requests.get(base_URL)
# activate video feed is necessary to run the camera ''' 
activate_camera_module_thread()

# Javascript is not ran by requests, so we have to start LED ourselves
print("starting the LED")
led_URL = base_URL + '/send_serial/?value=led_on&board=waterscope'
led_off_URL = base_URL + '/send_serial/?value=led_off&board=waterscope'
requests.get(led_URL)


print('switch to OPENCV')
OpenCV_URL = base_URL + '/change_stream_method/?stream_method=OpenCV'
OpenCV_URL_requests = requests.get(OpenCV_URL, headers = headers)
requests.get(base_URL)
activate_camera_module_thread()
time.sleep(2)

print('switch back to Picamera')
PiCamera_URL = base_URL + '/change_stream_method/?stream_method=PiCamera'
PiCamera_URL_requests = requests.get(PiCamera_URL, headers = headers)
requests.get(base_URL)
activate_camera_module_thread()
time.sleep(2)



print('start timelapse')
timelapse_URL = base_URL + '/acquire_data/?option=waterscope_timelapse_{0}&filename=raspberry_pi_time'.format(15)
requests.get(timelapse_URL, headers = headers)