crontab -e


@reboot sudo bash /home/pi/WaterScope-RPi/headless/start_headless.sh&
@reboot sudo bash /home/pi/WaterScope-RPi/headless/start_ML.sh&
@reboot sudo bash /home/pi/WaterScope-RPi/headless/bl_start.sh&
@reboot sudo bash /home/pi/WaterScope-RPi/sh_command/start_ngrok.sh&



