import requests
import time
import threading

''' this allows us to start autofocus and timelapse without using the browser'''

base_URL = "http://localhost:5000" 
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}


def activate_video_feed():
    ''' activate video feed is necessary to run the camera ''' 
    video_URL = base_URL + '/v'
    print('start camera')
    video_URL_requests = requests.get(video_URL, headers = headers)


print('starting the camera')
# activate video feed is necessary to run the camera ''' 
threading_video_feed = threading.Thread(target=activate_video_feed)
threading_video_feed.daemon = True
threading_video_feed.start()

# Javascript is not ran by requests
print("starting the LED")
led_URL = base_URL + '/send_serial/?value=led_on&board=waterscope'
time.sleep(2)

print('switch back to PiCamera')
auto_focus_URL = base_URL + '/auto_focus'
auto_focus_URL_requests = requests.get(auto_focus_URL+'/?status=start', headers = headers)
print('auto focusing ... ')
while True:
    #  use a way to determine the wait time
    time.sleep(5)
    print('still focusing...')
    auto_focus_URL_requests = requests.get(auto_focus_URL).json()
    if auto_focus_URL_requests['status'] == 'done':
        print('motor is ready')
        break

print('switch back to PiCamera')
PiCamera_URL = base_URL + '/change_stream_method/?stream_method=PiCamera'
PiCamera_URL_requests = requests.get(PiCamera_URL, headers = headers)

time.sleep(2)

print('start timelapse')
timelapse_URL = base_URL + '/acquire_data/?option=waterscope_timelapse_{0}&filename=raspberry_pi_time'.format(10)
requests.get(timelapse_URL, headers = headers)






    # openCV_URL = base_URL + '/change_stream_method/?stream_method=OpenCV'
    # requests.get(openCV_URL, headers = headers)
    # print('start opencv')
    # time.sleep(5)
    # print('start to focus?')
    # # while True:
    # #     requests.get(base_URL, headers=headers)
    # #     time.sleep(0.1)

    # timelapse_URL = base_URL + '/acquire_data/?option=waterscope_timelapse_{0}&filename=raspberry_pi_time'.format(3)
    # requests.get(timelapse_URL, headers = headers)

    # print('timelapse has started..')