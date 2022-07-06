import json
import re
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import MySQLdb.cursors
from dronelib.server import create_server
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
from utils import send_verification_email
from flask_jwt_extended import get_jwt_identity, JWTManager, verify_jwt_in_request, get_jwt, decode_token
from uploads.config import drone

UPLOAD_FOLDER = 'C:/Users/SIKIRU/Desktop/Droneproject/Groundstationapp/uploads'
ALLOWED_EXTENSIONS = {'json', 'py'}

app = Flask(__name__)

# IP AND PORT ARE STATIC SO NO NEED TO SET EVERYTIME
gcs = create_server('127.0.0.1', 9999)

# -----------database setup------------
app.secret_key = "my/secret/key/2795/17/132/moh"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '00Apassword7'
app.config['MYSQL_DB'] = 'aerolab'
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
jwt = JWTManager(app)
db = MySQL(app)


# --------------user and login------------------------------------
@app.route('/')
@app.route('/home', methods=["GET", "POST"])
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
            if account['email_verified']:
                msg = 'Logged in successfully !'
                return render_template('base.html', msg=msg)
            else:
                msg = 'email not verified!'
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
        email_verified = False
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
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s,% s)',
                           (username, password, email, email_verified))
            db.connection.commit()
            send_verification_email(email, username)
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/email-verification', methods=['GET', 'POST'])
def email_verification():
    if request.args['token'] and request.args['email']:
        token = request.args.get('token')
        email = request.args.get('email')
        claims = decode_token(encoded_token=token)
        if claims["is_admin"]:
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE accounts SET email_verified = 1 WHERE email = % s', (email,))
            db.connection.commit()
            return jsonify(f"email verification successful for :{email}")
        else:
            return jsonify("email-verification failed, contact Admin")


# -------------- setup server-------------------------
@app.route('/connect', methods=["GET", 'POST'])
def connect_ground_station():
    number = drone['number']
    if request.method == "POST":
        gcs.create_socket()
        gcs.accept_conn(int(number))
        flash("server connected successfully")
        return render_template('base.html')


# -----------send command------------------------------
@app.route('/commands', methods=["GET", "POST"])
def send_commands():
    if request.method == "POST":
        cmd = request.form.get("cmd")
        if cmd == 'arm':
            cmd = f"""{cmd}{drone['alt']}"""
            gcs.send_commands(cmd)
            flash("operation success")
            return render_template('base.html')
        else:
            gcs.send_commands(cmd)
            flash("operation success")
            return render_template('base.html')


# ----------------select drone---------------------
@app.route('/select', methods=["GET", "POST"])
def select_drone():
    if request.args['drone-id'] and request.args['cmd']:
        number = request.args.get('drone-id')
        cmd = request.args.get('cmd')
        gcs.get_target(number, cmd)
        flash("operation success")
        return render_template("base.html")


@app.route('/home/addresses', methods=["GET", "POST"])
def address():
    msg = (len(gcs.all_addresses), gcs.all_addresses)
    return render_template('base.html', msg=msg)


# -------------stream telemetry---------------
@app.route("/recv", methods=["GET", 'POST'])
def recv_telem():
    if request.method == "POST":
        data = request.get_json()
        telemetry = json.dumps(data)
        with open('TELEMETRY_FILE', 'w') as f:
            f.write(telemetry)
        return render_template('base.html', msg='telemetry streaming in progress')


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
        if file.filename == 'paths.json':
            gcs.upload_path()
            flash("PathFile upload successful")
            return render_template('base.html')
        if file.filename == 'config.py':
            flash("ConfigFile upload successful")
            return render_template('base.html')


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5003)
