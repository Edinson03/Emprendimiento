from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from functools import wraps
import string
from passlib.hash import pbkdf2_sha256


app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'  # Cambia esto a una clave segura y secreta

#Database
client = pymongo.MongoClient('mongodb://localhost:27017/users')
db = client.user_login


@app.route('/agregar',methods=['POST'])
def agregar():
    if request.method == 'POST':
        
        date = {
            'placa'  : request.form.get('placa'),
            'modelo' : request.form.get('modelo'),
            'marca' : request.form.get('marca'),
            'fecha'  : request.form.get('fecha'),
            'descripcion'  : request.form.get('descripcion'),
   
        }
        

        # Insertar el usuario en la base de datos
        db.db.motos.insert_one({
            'placa'  : date['placa'],
            'modelo' : date['modelo'],
            'marca' : date['marca'],
            'fecha'  : date['fecha'],
            'descripcion'  : date['descripcion'],

        })
        
        return redirect(url_for('menu'))


    return render_template('index.html', validacion = None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['POST', 'GET'])
def buscar():
    return render_template('menu.html')

@app.route('/cuenta', methods=['POST', 'GET'])
def cuenta():
    return render_template('adcuenta.html')

@app.route('/cerrar')
def cerrar():
    session.clear()
    return redirect('/')

@app.route('/registrar',methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        
        date = {
            'name'  : request.form.get('name'),
            'email' : request.form.get('email'),
            'phone' : request.form.get('phone'),
            'date'  : request.form.get('date'),
            'password'  : request.form.get('password'),
            
            # Get data from the card details section
            'plan': request.form.get('plan'),
            'nameT' : request.form.get('nameT'),
            'number' : request.form.get('number'),
            'fecha' : request.form.get('fecha'),
            'ccv'   : request.form.get('ccv'),
   
        }
        
        confirm = request.form.get('confirm')
        
        print(date)
        # Password verification
        validacion = validateCustomer(date, confirm) 
        print(validacion)
        if validacion:
            return render_template('registro.html', validacion= validacion)

                # Verificar si el usuario ya existe en la base de datos
        if db.db.usuarios.find_one({'email': date['email']}):
            return 'Usuario ya registrado. <a href="/registro">Intentar nuevamente</a>'

        # Cifrar la contraseña antes de almacenarla en la base de datos
            # Encrypt the password
        date['password'] = pbkdf2_sha256.encrypt(date['password'])

        # Add your database logic or other actions here

        print(date)
        # Insertar el usuario en la base de datos
        db.db.usuarios.insert_one({
            'name'  : date['name'],
            'email' : date['email'],
            'phone' : date['phone'],
            'date'  : date['date'],
            'password'  : date['password'],
            
            # Get data from the card details section
            'plan': date['plan'],
            'nameT' : date['nameT'],
            'number' : date['number'],
            'fecha' : date['fecha'],
            'ccv'   : date['ccv'],
        })
        
        return redirect(url_for('menu'))


    return render_template('registro.html', validacion = None)

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    return render_template('dashboard.html')

@app.route('/inicio', methods=['POST', 'GET'])
def inicio():
    if request.method == 'POST':
        correo = request.form['email']
        contraseña = request.form['password']

        
        user = db.db.usuarios.find_one({
        "email": request.form.get('email')
        })
    
        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return redirect(url_for('menu'))
        else:
            return render_template('inicio.html', validacion = 'No se pudo conectar')
            
    return render_template('inicio.html')


 
def validateCustomer(customer, confirm):
    print(customer)
    error_message = None
    
    # Validar Usuario
    if not customer['name']:
        error_message = "Please Enter your First Name !!"
    elif len (customer['name']) < 3:
        error_message = 'First Name must be 3 char long or more'
    elif not customer['phone']:
        error_message = 'Enter your Phone Number'
    elif len (customer['phone']) < 10:
        error_message = 'Phone Number must be 10 char Long'
    elif len (customer['password']) < 7:
        error_message = 'Password must be 7 char long'
    elif not any([char.isdigit() for char in customer['password']]):
        error_message = 'Password requires a digit'
    elif not any([char.isupper() for char in customer['password']]):
        error_message = 'Password requires a capital'
    elif not any([True if char in string.punctuation else False for char in customer['password']]):
        error_message = 'Password requires a special character'
    elif len (customer['email']) < 5:
        error_message = 'Email must be 5 char long'
    elif customer['password'] != confirm:
        error_message  = 'The passwords do not match'
    # saving
    return error_message


if __name__ == '__main__':
    app.run(debug=True)
