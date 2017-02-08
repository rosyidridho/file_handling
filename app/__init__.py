from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

#create an instance of flask
app = Flask(__name__)

#include config from config.py
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = 'app/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['html', 'py'])
app.secret_key = 'some_secret'

#create an instance of SQLAlchemy
db = SQLAlchemy(app)
from app import models, views
