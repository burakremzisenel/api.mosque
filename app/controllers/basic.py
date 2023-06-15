#!/usr/bin/env python
# coding: latin1
from flask import Blueprint, jsonify, request
import json
from config import app
from flask_cors import CORS

class ThreatStackError(Exception):
    '''Base Threat Stack error.'''
    status_code = 500

class ThreatStackRequestError(ThreatStackError):
    '''Threat Stack request error.'''

class ThreatStackAPIError(ThreatStackError):
    '''Threat API Stack error.'''

CORS(app)
#pip install -U flask-cors

blueprint = Blueprint('basic', __name__)
   
""" apple-app-site-association """
@blueprint.route('/apple-app-site-association', methods=['GET'])
def get_ios():
    if request.method == 'GET':
        data = {
                "applinks": {
                    "apps": [],
                    "details": [
                    {
                        "appID": app.config['APP_ID'],
                        "paths": [ "*" ],
                        "components": [
                        {
                            "/": "*"
                        }
                        ]
                    }
                    ]
                }
                }
  
        return jsonify(data)
@blueprint.route('/.well-known/apple-app-site-association', methods=['GET'])
def get_ios_well_known():
    if request.method == 'GET':
        data = {
                "applinks": {
                    "apps": [],
                    "details": [
                    {
                        "appID": app.config['APP_ID'],
                        "paths": [ "*" ],
                        "components": [
                        {
                            "/": "*"
                        }
                        ]
                    }
                    ]
                }
                }
  
        return jsonify(data)
