from flask import Flask
from flask_sqlalchemy import SQLAlchemy


#create an instance of flask
app = Flask(__name__)

#create an instance of SQLAlchemy
db = SQLAlchemy(app)

#include config from config.py
app.config.from_object('config')

app.config['UPLOAD_FOLDER'] = 'app/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'doc', 'docx', 'pdf', 'zip', 'rar', 'odt', 'jpg', 'JPG', 'png', 'PNG', 'mp4', 'mp3', 'vlc', 'MP4', 'deb', 'mkv', 'webm', 'gz'])
app.secret_key = 'some_secret'


from app import models, views
