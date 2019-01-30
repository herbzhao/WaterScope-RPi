import os
from datetime import datetime
import time


def set_pi_time(user_time):
    # format is 2019-01-30 21:53:00 UTC
    os.system('sudo date --set "{}"'.format(user_time))
