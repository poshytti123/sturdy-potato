from flask import Flask, request, g, render_template, make_response,  abort, redirect, url_for

import sqlite3
import os
DATABASE = os.path.join(os.getcwd(), 'database.db')

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def migrate_if_not_exists(version):
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id FROM migration WHERE id=?", (version,))
            migration_exists = cursor.fetchone() is not None
        except sqlite3.OperationalError:
            # If the alembic_version table does not exist, the migration has not been run.
            migration_exists = False
        finally:
            cursor.close()
            conn.close()
        if not migration_exists:
            print(f"Running migration {version}")
            init_db();
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

def get_user_id(db, username):
    cursor = db.execute("SELECT id FROM users WHERE username = ? ", (username,))
    return cursor.fetchone()[0]

def get_all_airports(db):
    cursor = db.execute("SELECT * FROM airports")
    return cursor.fetchall()


def get_all_flights(db, from_airport, to_airport, date):
    #cursor = db.execute("SELECT * FROM flights WHERE from_airport = ? and to_airport = ?  and date(departure) = date(?)", (from_airport, to_airport, date))
    cursor = db.execute("""
    SELECT
    f.id,
    f.from_airport,
    f.to_airport,
    f.departure,
    f.arrival,
    f.available_tickets - COALESCE(SUM(b.tickets_count), 0)
    AS
    available_tickets
FROM
flights
f
LEFT
JOIN
booking
b
ON
f.id = b.flight_id
AND
b.booking_status = 1
WHERE
f.from_airport = ? and f.to_airport = ? and date(f.departure) = date(?)
GROUP BY f.id, f.from_airport, f.to_airport, f.departure, f.arrival, f.available_tickets
""", (from_airport, to_airport, date));
    return cursor.fetchall()

def create_booking(db, flight_id, user_id, tickets_count):
    print(flight_id, user_id, tickets_count)
    db.execute("INSERT INTO booking (user_id,flight_id,booking_status,tickets_count) VALUES (?,?,?,?)" , (user_id, flight_id, 1, tickets_count))
    db.commit()


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
    resp = make_response(render_template('user_created.html'), 200)
    resp.set_cookie('username', request.form['username'])
    return resp

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


@app.route('/search', methods=['GET'])
def search_view():
    username = request.cookies.get('username')

    db = get_db()

    ap = get_all_airports(db)
    print(f"Airports: {ap}")
    from_airport  = request.args.get('from_airport', '')
    to_airport = request.args.get('to_airport', '')
    date = request.args.get('date', '')
    print(from_airport, to_airport, date)
    if(from_airport != '' and to_airport != '' and date != ''):
        flights = get_all_flights(db,from_airport, to_airport, date)
        print(flights)
    else:
        flights = []
    return render_template('search.html'
                           , from_airport = ap
                           , to_airport = ap
                           , date = date
                           , selected_from_airport = from_airport
                           , selected_to_airport = to_airport
                           , flights = flights
                           )



@app.route('/book', methods=['GET'])
def book_view():
    username = request.cookies.get('username')
    if username == '' or username == None:
        print('cookie was empty')
        return redirect(url_for('login'))
    else:
        db = get_db()
        user_id = get_user_id(db,username)
        if user_id == 0 or user_id == None:
            print('user_id was empty')
            return redirect(url_for('login'))
        flight_id = request.args.get('flight_id', '')
        tickets_count = request.args.get('tickets_count', 1)
        if flight_id == '' or flight_id == None:
            return redirect(url_for('search'))
        create_booking(db,flight_id,user_id, tickets_count)
        return render_template('book.html'
                               )



if __name__ == '__main__':
    #init_db()
    migrate_if_not_exists(1);
    app.run(host="0.0.0.0", port=8080, debug=True)
