import os
from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from werkzeug import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['html', 'py'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/upload_handling', methods = ['POST'])
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

@app.route('/files/delete_item/<filename>', methods=['GET', 'POST'])
def delete_handling(filename):
    try:

        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('list_files')) #('Deleted')
    except Exception as e:
        return {'error': str(e)}


@app.route('/files', methods = ['GET'])
def list_files():
    path = os.path.expanduser(u'uploads/')
    return render_template('files.html', tree=make_tree(path))

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
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
