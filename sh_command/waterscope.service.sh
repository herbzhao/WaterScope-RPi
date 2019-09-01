[Unit]
Description=Gunicorn instance to serve api
After=network.target

[Service]
User=root
ExecStart=/usr/local/bin/gunicorn --threads 10  --bind 0.0.0.0:80  app:app
WorkingDirectory=/home/pi/WaterScope-RPi/web_interface
StandardOutput=inherit
StandardError=inherit
Restart=always

[Install]
WantedBy=multi-user.target
