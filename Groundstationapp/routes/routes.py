import re
import time
from . import blueprint
from flask import render_template, request, redirect, url_for, session, flash, jsonify
import MySQLdb.cursors
from Groundstationapp.dronelib.server import create_server
import os
from werkzeug.utils import secure_filename
from Groundstationapp.utils import send_verification_email
from Groundstationapp.uploads.config import param
from flask_jwt_extended import decode_token
from Groundstationapp.application import app
from Groundstationapp.application import db

ALLOWED_EXTENSIONS = {'json', 'py'}
gcs = create_server('192.168.247.223', 9999)

telemetry = []


# --------------user and login------------------------------------
@blueprint.route('/')
@blueprint.route('/login', methods=["GET", "POST"], endpoint='login')
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


@blueprint.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('routes.login'))


@blueprint.route('/register', methods=['GET', 'POST'])
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


@blueprint.route('/email-verification', methods=['GET', 'POST'])
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
@blueprint.route('/connect', methods=["GET", 'POST'])
def connect_ground_station():
    number = param['number']
    if request.method == "POST":
        gcs.create_socket()
        gcs.accept_conn(int(number))
        gcs.transform_ip()
        flash("server connected successfully")
        return redirect(url_for('routes.send_telemetry'))  # render_template('base.html')


# -----------send command------------------------------
@blueprint.route('/commands', methods=["GET", "POST"])
def send_commands():
    if request.method == "POST":
        cmd = request.form.get("cmd")
        if cmd == 'arm':
            cmd = f"""{cmd}{param['alt']}"""
            gcs.send_commands(cmd)
            flash("operation success")
            return redirect(url_for('routes.send_telemetry'))
        else:
            gcs.send_commands(cmd)
            flash("operation success")
            return redirect(url_for('routes.send_telemetry'))


# ----------------select drone---------------------
@blueprint.route('/select', methods=["GET", "POST"])
def select_drone():
    if request.method == "POST":
        number = request.form.get('drone-id')
        cmd = request.form.get('cmd')
        gcs.get_target(number, cmd)
        flash("operation success")
        return redirect(url_for('routes.send_telemetry'))


@blueprint.route('/addresses', methods=["GET", "POST"])
def address():
    msg = (len(gcs.all_connections), gcs.new)  # gcs.all_connections, gcs.all_addresses, )
    return redirect(url_for('routes.send_telemetry', msg=msg))


# -------------stream telemetry---------------
@blueprint.route("/recv", methods=["GET", 'POST'])
def recv_telem():
    telemetry.clear()
    print(telemetry)
    if request.method == "POST":
        tele = request.get_json()
        telemetry.append(tele)
        print(telemetry)

        return "telemetry streaming in progress"


@blueprint.route('/telemetry', methods=["GET", 'POST'])
def send_telemetry():
    print('sending')
    return render_template('base.html', data=telemetry)  # jsonify(telemetry)


# ----------------------file upload------------------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route('/upload', methods=['GET', 'POST'])
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
