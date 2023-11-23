from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from flask_bcrypt import Bcrypt
from functools import wraps
bcrypt = Bcrypt()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'  # Cambia esto a una clave segura y secreta

# Database
#client = pymongo.MongoClient('mongodb://localhost:27017/users')
#db = client.user_login

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
