from flask import Flask
from routes import blueprint
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager
from uploads.config import MYSQL


UPLOAD_FOLDER = 'C:/Users/SIKIRU/Desktop/Droneproject/Groundstationapp/uploads'

app = Flask(__name__)

# # -----------database setup------------
app.secret_key = "my/secret/key/2795/17/132/moh"
app.config['MYSQL_HOST'] = MYSQL['host']
app.config['MYSQL_USER'] = MYSQL['user']
app.config['MYSQL_PASSWORD'] = MYSQL['password']
app.config['MYSQL_DB'] = MYSQL['database']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
jwt = JWTManager(app)
db = MySQL(app)
# # -----------blueprint for routes----------
app.register_blueprint(blueprint)


if __name__ == '__main__':
    app.run(host="192.168.247.223", port=5003)
