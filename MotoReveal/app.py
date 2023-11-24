from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from flask_bcrypt import Bcrypt
from functools import wraps
bcrypt = Bcrypt()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'  # Cambia esto a una clave segura y secreta

#Database
client = pymongo.MongoClient('mongodb://localhost:27017/users')
db = client.user_login

@app.route('/', )
def index():
    return render_template('index.html')

@app.route('/inicio', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contrasena']

        # Buscar el usuario en la base de datos
        usuario_encontrado = db.db.usuarios.find_one({'correo': correo})

        if usuario_encontrado and 'contraseña' in usuario_encontrado:
            # Verificar la contraseña con check_password_hash
            if bcrypt.check_password_hash(usuario_encontrado['contraseña'], contraseña.encode('utf-8')):
                session['correo'] = correo
                return redirect(url_for('home'))

    return render_template('inicio.html')


@app.route('/registrar',methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        usuario = request.form['name']
        correo = request.form['email']
        contraseña = request.form['password']

        # Verificar si el usuario ya existe en la base de datos
        if db.db.usuarios.find_one({'correo': correo}):
            return 'Usuario ya registrado. <a href="/registro">Intentar nuevamente</a>'

        # Cifrar la contraseña antes de almacenarla en la base de datos
        contraseña_cifrada = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())


        print(usuario,correo,contraseña)
        # Insertar el usuario en la base de datos
        db.db.usuarios.insert_one({
            'usuario': usuario,
            'correo': correo,
            'contraseña': contraseña_cifrada
        })
        session['logged_in'] = True
        return redirect(url_for('home'))

    return render_template('registro.html')

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')





if __name__ == '__main__':
    app.run(debug=True)
