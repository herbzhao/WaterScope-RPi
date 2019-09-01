#sudo gunicorn --threads 10 --workers 1 --bind 0.0.0.0:5000 app:app
cd /home/pi/WaterScope-RPi/web_interface
sudo gunicorn --threads 10  --bind 0.0.0.0:80  app:app
