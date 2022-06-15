from flask import Flask, render_template, request
from dronelib.server import create_server

application = Flask(__name__)

# IP AND PORT ARE STATIC SO NO NEED TO SET EVERYTIME
gcs = create_server('127.0.0.1', 9999)


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/')
def connect_ground_station():
    number = request.args.get("number_of_drones")
    gcs.create_socket()
    gcs.accept_conn(number)
    return 'socket server created successfully'


@application.route('/command/<cmd>')
def send_commands(cmd):
    gcs.send_commands(cmd)


if __name__ == '__main__':
    application.run(host="127.0.0.1", port=5003)
