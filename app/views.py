import os
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, session, g, flash
from werkzeug import secure_filename
from app import app, db
from app.models import Akun
from functools import wraps

app.config['UPLOAD_FOLDER'] = 'app/uploads/'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENSIONS']

def read_session(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        session.permanent = True
        try:
            if session['user'] is False:
                flash('Username or Password is invalid')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        except KeyError:
            flash('Your Session is time out, login first')
            return redirect(url_for('index'))
    return wrap

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session.pop('user', None)

        username = request.form['username']
        password = request.form['password']
        reg = Akun.query.filter_by(username=username,password=password).first()
        if reg is None:
            flash('Username or Password is invalid' , 'error')
            return redirect(url_for('index'))
        else:
            session['user'] = request.form['username']
            #login_user(registered_user)
            flash('Logged in successfully')
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        akun=Akun(request.form['username'], request.form['email'], request.form['password'])
        db.session.add(akun)
        db.session.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
def loguot():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/home')
@read_session
def home():
    return render_template('home.html')

@app.route('/upload')
@read_session
def upload():
    return render_template('upload.html')

@app.route('/upload_handling', methods = ['POST'])
@read_session
def upload_handling():
    try:
        file = request.files['file']
        if file and not allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('list_files'))
        else:
            return ('Ekstensi file tidak diperbolehkan')
    except Exception as e:
        return {'error': str(e)}

@app.route('/files/view/<filename>', methods=['POST', 'GET'])
@read_session
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/files/delete_item', methods = ['GET', 'POST'])
@read_session
def delete_handling():
    if request.method == 'POST':
        filename = request.form['filename']
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('list_files')) #('Deleted')
        except Exception as e:
            return {'error': str(e)}

@app.route('/files', methods = ['GET'])
@read_session
def list_files():
    path = os.path.expanduser(u'app/uploads/')
    return render_template('files.html', tree=make_tree(path))

def make_tree(path):
    i=0
    tree = dict(name=os.path.basename(path), children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                i=i+1
                tree['children'].append(dict(name=name, i=i))
    return tree
