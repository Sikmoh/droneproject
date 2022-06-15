from flask import Flask, render_template, request

from dronelib.server import create_server

application = Flask(__name__)

# IP AND PORT ARE STATIC SO NO NEED TO SET EVERYTIME
gcs = create_server('127.0.0.1', 9999)


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/', methods=["GET", 'POST'])
def connect_ground_station():
    if request.method == "POST":
        number = request.form.get("number_of_drones")
        gcs.create_socket()
        gcs.accept_conn(number)
        #return render_template("send.html")


@application.route('/commands', methods=["GET", "POST"])
def send_commands():
    if request.method == "POST":
        cmd = request.form.get("command")
        gcs.send_commands(cmd)
        #return render_template("form.html")


if __name__ == '__main__':
    application.run(host="127.0.0.1", port=5003)
