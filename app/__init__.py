from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#create an instance of flask
app = Flask(__name__)

#create an instance of SQLAlchemy
db = SQLAlchemy(app)
app.secret_key = 'some_secret'
app.config.from_object('config')

from app import models, views
