
from flask import Flask, render_template, Response, redirect, request, jsonify
import datetime

app = Flask(__name__)


''' The feed for serial_command output ''' 
@app.route('/')
def test_api_server():
    if datetime.datetime.now().second%2 == 0:
        motor_idle = True
    else:
        motor_idle = False
    return jsonify({'x':motor_idle, 'y':123})



if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)