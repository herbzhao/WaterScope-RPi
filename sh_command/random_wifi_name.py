import random
import subprocess

unique_ID = random.randint(10**8,10**9-1)
command = "sudo sed -i 's/WaterScope_WiFi/WaterScope_Wifi_{}/g' hostapd.conf".format(unique_ID)
print(command)

#subprocess.Popen(command)
