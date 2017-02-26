from app import db
from datetime import datetime

class Tb_akun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(150))
    level = db.Column(db.Integer, default=0)
    date_reg = db.Column(db.DateTime)

    def __init__(self, first_name, last_name, username, email, password, level, date_reg):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = password
        self.level = level
        if date_reg is None:
            date_reg = datetime.utcnow()
        self.date_reg = date_reg

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.username)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Tb_file(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    akun_id = db.Column(db.Integer, db.ForeignKey('tb_akun.id'))
    akun = db.relationship('Tb_akun', backref=db.backref('tb_file', lazy='dynamic'))
    filename = db.Column(db.String(100))
    size = db.Column(db.String(20))
    date_create = db.Column(db.DateTime)

    def __init__(self, akun_id, filename, size, date_create):
        self.akun_id = akun_id
        self.filename = filename
        self.size = size
        if date_create is None:
            date_create = datetime.utcnow()
        self.date_create = date_create
