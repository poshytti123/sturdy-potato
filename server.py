from flask import Flask, request, g, render_template, make_response

import sqlite3
import os
DATABASE = os.path.join(os.getcwd(), 'database.db')

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')

@app.route('/echo', methods=['GET'])
def echo():
    return {key: value for key, value in request.headers.items()}

@app.route('/info', methods=['GET'])
def info():
    return render_template('info.html')

@app.route('/echo', methods=['POST'])
def echo_post():
    return request.form

def check_if_user_exists(db, username):
    cursor = db.execute("SELECT * FROM users WHERE username = ? ", (username,))
    return cursor.fetchall()


def sign_in(db, username, password):
    cursor = db.execute("SELECT * FROM users WHERE username = ? and password = ? ", (username, password, ))
    return cursor.fetchall()


@app.route('/register', methods=['POST'])
def register():
    
    required_keys = {'username', 'password'}
    if not all(key in request.form for key in required_keys):
        return 'Missing username or password', 400

    username = request.form['username']
    password = request.form['password']
    
    if username == '' or password == '':
        return 'Invalid username or password', 400
    
    if username.isdigit():
        return render_template('register_Invalid username or password.html')

    db = get_db()
    if check_if_user_exists(db, username):
        return render_template('register_User already exists.html')

    db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    db.commit()
    
    return render_template('user_created.html')


@app.route('/login', methods=['POST'])
def login():
    
    required_keys = {'username', 'password'}
    if not all(key in request.form for key in required_keys):
        return 'Missing username or password', 400

    if(request.form['username'] == '' or request.form['password'] == ''):
        return 'Invalid username or password', 400
    
    db = get_db()
    
    if(sign_in(db, request.form['username'], request.form['password'])):
        resp =  make_response(render_template('profile.html', name = request.form['username']), 200)
        resp.set_cookie('username', request.form['username'])
        return resp
    
    return render_template('login_Invalid username or password copy.html')


@app.route('/register', methods=['GET'])
def register_view(): 
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def login_view(): 
    username = request.cookies.get('username')
    if username == '' or username == None:
        return render_template('login.html')
    else:
        return render_template('profile.html', name = username)


@app.route('/logout', methods=['GET'])
def logout(): 
    resp =  make_response(render_template('login.html'), 200)
    resp.set_cookie('username', '')
    return resp

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
