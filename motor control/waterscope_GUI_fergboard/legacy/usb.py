import os
usb_root_path = r"/media/pi/" + os.listdir("/media/pi")[0] + '/'
# make new directory
os.mkdir(usb_root_path + 'test')