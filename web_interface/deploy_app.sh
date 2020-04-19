#sudo gunicorn --threads 10 --workers 1 --bind 0.0.0.0:5000 app:app
sudo gunicorn --threads 5 --workers 1 --bind 0.0.0.0:80 app:app
