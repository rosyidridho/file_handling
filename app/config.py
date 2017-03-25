from flask_sqlalchemy import SQLAlchemy
import json
import os

DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
FILE_CONFIG = os.path.join(DIR,'config.json')

try:
    with open(FILE_CONFIG) as config:
        data_json = json.loads(config.read())
except Exception as e:
    raise e

UPLOAD_FOLDER = os.path.join(DIR, data_json["upload_folder"])
ALLOWED_EXTENSIONS = data_json["allowed_extensions"]
