import json
import re
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash
import MySQLdb.cursors
from dronelib.server import create_server
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'C:/Users/SIKIRU/Desktop/Droneproject/Groundstationapp/dronelib'
ALLOWED_EXTENSIONS = {'json'}

app = Flask(__name__)

# IP AND PORT ARE STATIC SO NO NEED TO SET EVERYTIME
gcs = create_server('127.0.0.1', 9999)

# -----------database setup------------
app.secret_key = "my-secret-key"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '00Apassword7'
app.config['MYSQL_DB'] = 'aerolab'

db = MySQL(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --------------user and login------------------------------------
@app.route('/')
@app.route('/login', methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('base.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
            db.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


# -------------- setup server-------------------------
@app.route('/connect', methods=["GET", 'POST'])
def connect_ground_station():
    if request.method == "POST":
        number = request.form.get("number_of_drones")
        gcs.create_socket()
        gcs.accept_conn(number)


# -----------send command------------------------------
@app.route('/commands', methods=["GET", "POST"])
def send_commands():
    if request.method == "POST":
        cmd = request.form.get("command")
        gcs.send_commands(cmd)


# ----------------select drone---------------------
@app.route('/select', methods=["GET", "POST"])
def select_drone():
    if request.method == "POST":
        number = request.form.get("drone-id")
        if request.form.get("return") == 'rtn':
            gcs.get_target(number, "RTL")
        elif request.form.get("land") == "land":
            gcs.get_target(number, "land")
        elif request.form.get("disarm") == "disarm":
            gcs.get_target(number, "disarm")
        return render_template("base.html")


# -------------stream telemetry---------------
@app.route("/recv", methods=["GET", 'POST'])
def recv_telem():
    if request.method == "POST":
        data = request.get_json()
        telemetry = json.dumps(data)
        with open('TELEMETRY_FILE', 'w') as f:
            f.write(telemetry)
        return 'streaming telemetry'


# ----------------------file upload------------------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            gcs.upload_path()
            return render_template('base.html')


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5003)
