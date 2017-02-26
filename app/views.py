import os, stat
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, session, g, flash
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.models import Tb_akun, Tb_file
from functools import wraps
from datetime import datetime, date


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENSIONS']

def cek_level(id_user):
    filter_akun = Tb_akun.query.filter_by(id=id_user).first()
    level = filter_akun.level
    return level

def read_session(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        session.permanent = True
        try:
            if session['user_id'] is False:
                flash('Username or Password is invalid')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        except KeyError:
            flash('Your Session is time out, login first')
            return redirect(url_for('index'))
    return wrap

def read_level(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if cek_level(session['user_id']) != 2:
            return 'xxxxxxx'
        return f(*args, **kwargs)
    return wrap

@app.route('/login', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        #password = request.form['password']
        '''test = Tb_akun.query.filter_by(username=username).first()
        cek = check_password_hash(test.password, request.form['password'])
        print cek'''
        cek_akun = Tb_akun.query.filter_by(username=username).first()
        if cek_akun is None:
            flash('Account not found' , 'error')
            return redirect(url_for('index'))
        else:
            cek_password = check_password_hash(cek_akun.password, request.form['password'])
            if cek_password is False:
                flash('Password is invalid' , 'error')
                return redirect(url_for('index'))
            else:
                session['user_id'] = str(cek_akun.id)
                return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        cek_akun = Tb_akun.query.filter_by(username=request.form['username']).first()
        if cek_akun is None:
            akun=Tb_akun(first_name=request.form['firstname'], last_name=request.form['lastname'], username=request.form['username'], \
            email=request.form['email'], password=generate_password_hash(request.form['password']), level=0, date_reg = datetime.utcnow())
            db.session.add(akun)
            db.session.commit()
            cek_akun = Tb_akun.query.filter_by(username=request.form['username']).first()
            foldername = str(cek_akun.id)
            os.mkdir('app/uploads/'+foldername)
            flash('New account was successfully created')
            return redirect(url_for('index'))
        else:
            flash('Username already exist, please insert another username')
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/logout')
def loguot():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/')
@read_session
def home():
    if cek_level(session['user_id']) == 2:
        tot_ac = tot_acc()
        tot_fl = tot_file()
        tot_strg = tot_storage()
        acc_inactv = tot_acc_inactive()
        return render_template('dash-admin.html', tot_akun=tot_ac, tot_file=tot_fl, tot_strg=tot_strg, acc_inactv=acc_inactv)
    else:
        return render_template('home.html')

def tot_acc():
    akun = Tb_akun.query.all()
    i=0
    for ak in akun:
        i=i+1
    return i

def tot_file():
    files = Tb_file.query.all()
    i=0
    for fl in files:
        i=i+1
    return i

def tot_storage():
    storage = Tb_file.query.all()
    i=0
    for strg in storage:
        i=i+int(strg.size)
    return convert_size(i)

def tot_acc_inactive():
    acc_inactive = Tb_akun.query.filter_by(level=0)
    i=0
    for ak in acc_inactive:
        i=i+1
    return i

@app.route('/upload')
@read_session
def upload():
    return render_template('upload.html')

@app.route('/upload_handling', methods = ['POST'])
@read_session
def upload_handling():
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            cek_file = Tb_file.query.filter_by(filename=filename)
            for nm_file in cek_file:
                if nm_file.filename == filename:
                    flash ('Nama File sudah ada')
                    return redirect(url_for('upload'))

            direktori = app.config['UPLOAD_FOLDER']+str(session['user_id'])+"/"
            file.save(os.path.join(direktori, filename))
            filesize = os.path.getsize(direktori+filename)
            print filesize
            ins_file=Tb_file(akun_id=str(session['user_id']), filename=filename, size=str(filesize), date_create=datetime.utcnow())
            db.session.add(ins_file)
            db.session.commit()
            return redirect(url_for('list_files'))
        else:
            flash ('Ekstensi file tidak diperbolehkan')
            return redirect(url_for('upload'))
    except Exception as e:
        return {'error': str(e)}

@app.route('/view/<fn>', methods=['POST', 'GET'])
@read_session
def uploaded_file(fn):
    if request.method == 'POST':
        user_direktori = "../"+app.config['UPLOAD_FOLDER']+session['user_id']+"/"
        filename = request.form['filename']
        return  send_from_directory(user_direktori, filename)


@app.route('/files/delete_item', methods = ['GET', 'POST'])
@read_session
def delete_handling():
    if request.method == 'POST':
        user_direktori = app.config['UPLOAD_FOLDER']+session['user_id']+"/"
        filename = request.form['filename']
        try:
            os.remove(os.path.join(user_direktori, filename))
            del_item = Tb_file.query.filter_by(filename=filename)

            for item in del_item:
                del_file = Tb_file.query.get(item.id)
                db.session.delete(del_file)
                db.session.commit()
            return redirect(url_for('list_files')) #('Deleted')
        except Exception as e:
            return {'error': str(e)}

@app.route('/files', methods = ['GET'])
@read_session
def list_files():
    user_direktori = str(session['user_id'])
    path = os.path.expanduser(u'app/uploads/'+user_direktori)
    allfile = Tb_file.query.filter_by(akun_id=session['user_id'])
    tot_size = 0
    for item in allfile:
        tot_size = tot_size + int(item.size)
    total_size = convert_size(tot_size)
    return render_template('files.html', tree=make_tree(path), to_size=total_size)

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
                Osize = os.path.getsize(path+"/"+name)
                size = convert_size(Osize)
                tree['children'].append(dict(name=name, i=i, size=size))
    return tree


def convert_size(size):
    if size < 1000000:
        size = size / 1000
        newsize = str(size)+" Kb"
    elif size >= 1000000:
        size = size / 1000000
        newsize = str(size)+" Mb"
    return newsize

def owner(kode):
    cek = Tb_akun.query.filter_by(id=kode)
    ret = 'None'
    for c in cek:
        if kode == c.id:
            pemilik = Tb_akun.query.get(kode)
            ret = pemilik.username
        else:
            ret = 'None'

    return ret

@app.route('/users-data', methods=['POST', 'GET'])
@read_session
@read_level
def user_data():
    akunAll = Tb_akun.query.all()
    if request.method == 'POST':
        akun = Tb_akun.query.get(request.form['id_user'])
        akun.first_name = request.form['firstname']
        akun.last_name = request.form['lastname']
        db.session.commit()
    return render_template('admin/users-data.html', akun=akunAll)

@app.route('/users-files')
@read_session
@read_level
def user_file():
    path = os.path.expanduser(u'app/uploads/')
    return render_template('admin/users-files.html', tree=make_tree(path))

@app.route('/<id>')
@read_session
@read_level
def user_file_id(id):
    path = os.path.expanduser(u'app/uploads/'+id)
    kode = int(id)
    pemilik = owner(kode)

    return render_template('admin/users-files-id.html', tree=make_tree(path), foldername=id, pemilik=pemilik)

@app.route('/view-admin/<fn>', methods=['POST', 'GET'])
@read_session
@read_level
def view_admin(fn):
    if request.method == 'POST':
        foldername = request.form['foldername']
        filename = request.form['filename']
        direktori = "../"+app.config['UPLOAD_FOLDER']+foldername+"/"
        return send_from_directory(direktori, filename)

@app.route('/delete', methods = ['GET', 'POST'])
@read_session
@read_level
def delete():
    if request.method == 'POST':
        foldername = str(request.form['foldername'])
        filename = request.form['filename']
        direktori = app.config['UPLOAD_FOLDER']+foldername+"/"
        try:
            os.remove(os.path.join(direktori, filename))
            return redirect(url_for('user_file_id', id=foldername)) #('Deleted')
        except Exception as e:
            return {'error': str(e)}
