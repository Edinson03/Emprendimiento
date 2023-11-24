from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from flask_bcrypt import Bcrypt
from functools import wraps
import string
bcrypt = Bcrypt()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'  # Cambia esto a una clave segura y secreta

#Database
client = pymongo.MongoClient('mongodb://localhost:27017/users')
db = client.user_login

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['POST', 'GET'])
def buscar():
    return render_template('menu.html')

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
        
        date = {
            'name'  : request.form.get('name'),
            'email' : request.form.get('email'),
            'phone' : request.form.get('phone'),
            'date'  : request.form.get('date'),
            'password'  : request.form.get('password'),
   
        }
        
        confirm = request.form.get('confirm')
        
        print(date)
        # Password verification
        validacion = validateCustomer(date, confirm) 
        print(validacion)
        if validacion:
            return render_template('registro.html', validacion= validacion)

        # Get data from the card details section
        plan = request.form.get('plan')
        nameT = request.form.get('nameT')
        number = request.form.get('number')
        fecha = request.form.get('fecha')
        ccv = request.form.get('ccv')

        # Save the data to your database or perform any necessary actions
        # Here, we're just printing the data as an example
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Date: {date}")
        print(f"Plan: {plan}")
        print(f"Name on Card: {nameT}")
        print(f"Card Number: {number}")
        print(f"Expiration Date: {fecha}")
        print(f"CCV: {ccv}")

        # Add your database logic or other actions here

        return "Registration successful. Data has been processed."


    return render_template('registro.html', validacion = None)

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

def validateCustomer(customer, confirm):
    print(customer)
    error_message = None
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
    elif customer.isExists ():
        error_message = 'Email Address Already Registered..'
    elif customer['password'] != confirm:
        error_message  = 'The passwords do not match'
    # saving
    return error_message

if __name__ == '__main__':
    app.run(debug=True)
