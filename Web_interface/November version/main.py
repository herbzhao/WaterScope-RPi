debug_mode = True

from flask import Flask, render_template, request, jsonify, Response
import json
from werkzeug.datastructures import MultiDict


# debug mode 
if debug_mode is False:
    pass


app = Flask(__name__)



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, threaded=True)
