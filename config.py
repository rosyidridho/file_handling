from flask_sqlalchemy import SQLAlchemy
import json
import os

DIR = os.path.dirname(os.path.realpath(__file__))
FILE_CONFIG = os.path.join(DIR,'config.json')

try:
    with open(FILE_CONFIG) as config:
        data_json = json.loads(config.read())
except Exception as e:
    raise e

db_username = str(data_json["db"]["db_username"])
db_pass = str(data_json["db"]["db_pass"])
db_host = str(data_json["db"]["db_host"])
db_name = str(data_json["db"]["db_name"])
conn = "mysql://"+db_username+":"+db_pass+"@"+db_host+"/"+db_name

SQLALCHEMY_DATABASE_URI = conn
