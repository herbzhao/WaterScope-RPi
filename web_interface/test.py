import os
import datetime

starting_time = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
last_logged_temp = 1

if not os.path.exists("timelapse_data/arduino"):
    os.mkdir("timelapse_data/arduino")
if not os.path.exists("timelapse_data/arduino/{}".format(starting_time)):
    os.mkdir("timelapse_data/arduino/{}".format(starting_time))
log_file_location = "timelapse_data/arduino/{}/temp_log.txt".format(starting_time)
while True:
    with open(log_file_location, 'a+') as log_file:
        now = datetime.datetime.now()
        time_value_formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        try:
            last_logged_temp = 321
            if last_logged_temp:
                log_file.write(time_value_formatted)
                log_file.write('\n')
                log_file.write(str(123))
                log_file.write('\n')
                del(last_logged_temp)
        except:
            pass