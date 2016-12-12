# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 16:27:13 2016

@author: herbz
"""

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'