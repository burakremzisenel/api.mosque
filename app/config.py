#!/usr/bin/env python
# coding: latin1
import os
import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from firebase_admin import credentials

app = Flask(__name__)

app.config["FIREBASE_ADMIN_CREDENTIAL"] = credentials.Certificate("mosque-adminsdk.json")
app.config["FIREBASE_ADMIN_AUTHORIZATION_SCHEME"] = "JWT"
app.config["FIREBASE_ADMIN_CHECK_REVOKED"] = False  # don't check for revoked tokens
app.config["FIREBASE_ADMIN_PAYLOAD_ATTR"] = "firebase_jwt"

#config_obj = yaml.load(open('config.yaml'), Loader=yaml.Loader)
#app.config['PARAM_X'] = config_obj['PARAM_X'] if param_x is None else database_url

# override the environment variables
database_url = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['TIMEZONE'] = os.getenv('TZ')
#tz = timezone(app.config['TIMEZONE'])

app.config['API_KEY'] = os.getenv('API_KEY')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['APP_SIGNATURE'] = os.getenv('APP_SIGNATURE')
app.config['APP_ID'] = os.getenv('APP_ID')

app.config['UPLOAD_FOLDER'] = 'img'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['RESTPLUS_MASK_SWAGGER'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)