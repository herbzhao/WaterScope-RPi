crontab -e
@reboot sudo bash /home/pi/WaterScope-RPi/headless/start_headless.sh&
@reboot sudo bash /home/pi/WaterScope-RPi/headless/start_ML.sh&