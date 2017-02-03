import os
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, session, g
from werkzeug import secure_filename
'''from flask.ext.mysql import MySql
mysql = MySql()'''

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['html', 'py'])
app.secret_key = 'some_secret'

#MySql configurations
'''app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '20022013'
app.config['MYSQL_DATABASE_DB'] = 'db_file_handling'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session.pop('user', None)

        if request.form['password'] == '20022013':
            session['user'] = request.form['username']
            return redirect(url_for('home'))
    return render_template('login.html')

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/logout')
def loguot():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if g.user:
        return render_template('home.html')
    return redirect(url_for('index'))

@app.route('/upload')
def upload():
    if g.user:
        return render_template('upload.html')
    return redirect(url_for('index'))

@app.route('/upload_handling', methods = ['POST'])
def upload_handling():
    if g.user:
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
    return redirect(url_for('index'))

@app.route('/files/delete_item/<filename>', methods=['GET', 'POST'])
def delete_handling(filename):
    if g.user:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('list_files')) #('Deleted')
        except Exception as e:
            return {'error': str(e)}
    return redirect(url_for('index'))

@app.route('/files', methods = ['GET'])
def list_files():
    if g.user:
        path = os.path.expanduser(u'uploads/')
        return render_template('files.html', tree=make_tree(path))
    return redirect(url_for('index'))

def make_tree(path):
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
                tree['children'].append(dict(name=name))
    return tree

@app.route('/files/view/<filename>')
def uploaded_file(filename):
    if g.user:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
