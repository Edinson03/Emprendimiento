from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from functools import wraps
import string
from bson import ObjectId
from passlib.hash import pbkdf2_sha256

user_activo = ""


app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta'  # Cambia esto a una clave segura y secreta

#Database
#client = pymongo.MongoClient('mongodb+srv://revealmoto:3gdYFc0bKngQOK11@cluster0.g8e9qsh.mongodb.net/')
client = pymongo.MongoClient('mongodb://localhost:27017/users')
db = client.user_login

# Decorators
def login_require(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap


@app.route('/agregar',methods=['POST'])
@login_require
def agregar():
    if request.method == 'POST':
        
        date = {
            'placa'  : request.form.get('placa').upper(),
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


@app.route('/modificar', methods=['POST'])
@login_require
def modificar():
    
    if request.method == 'POST':
        date = {
            '_id' : request.form.get('_id'),
            'placa'  : request.form.get('placa'),
            'modelo' : request.form.get('modelo'),
            'marca' : request.form.get('marca'),
            'fecha'  : request.form.get('fecha'),
            'descripcion'  : request.form.get('descripcion'),
   
        }
        
        if date['_id'] != "" and date['placa'] != "" and date['modelo'] != "" and date['marca'] != "" and date['fecha'] != "" and date['descripcion'] != "":
            db.db.motos.update_one({ 
                '_id' : ObjectId (request.form.get('_id'))
            },{'$set' : {
                'placa'  : request.form.get('placa'),
                'modelo' : request.form.get('modelo'),
                'marca' : request.form.get('marca'),
                'fecha'  : request.form.get('fecha'),
                'descripcion'  : request.form.get('descripcion'),
               }
                
            }
            )
            return render_template('dashboard.html', error = "Datos Actualizados")
           
        return render_template('dashboard.html', error = "Llene todos los campos")
    return render_template('dashboard.html')

@app.route('/historial', methods=['POST'])
@login_require
def historial():
    if request.method == 'POST':
        
        data = db.db.motos.find({
            'placa': request.form.get('placa').upper()
        })
        data = list(data)
        print(request.form.get('placa'))
        print(data)
        return render_template('dashboard.html', placa =request.form.get('placa').upper(), data=data)
    return render_template('dashboard.html')

@app.route('/eliminar', methods=['POST'])
@login_require
def eliminar():
    
    if request.method == 'POST':
        
        db.db.motos.delete_one({
            '_id': ObjectId(request.form.get('_id'))
        })

        return render_template('dashboard.html', error= "Eliminacion Completa")
    return render_template('dashboard.html')

@app.route('/')
def index():
    return render_template('adcuenta.html')

# Gestion de la Cuenta


@app.route('/buscar', methods=['POST', 'GET'])
def buscar():
    if request.method == 'POST':
        data = db.db.motos.find({
            'placa': request.form.get('placa').upper()
        })
        data = list(data)
        print(request.form.get('placa'))
        print(data)
        return render_template('menu.html', placa =request.form.get('placa').upper(), data=data)
    return render_template('menu.html')


@app.route('/cuenta', methods=['POST', 'GET'])
def cuenta():
    
    data = db.db.usuarios.find_one({'email' : user_activo})
        
    print(user_activo, data)
    return render_template('adcuenta.html', data = data)

@app.route('/modificarcuenta', methods=['POST', 'GET'])
def modificarcuenta():
    if request.method == 'POST':
            db.db.usuarios.update_one({ 
                'email' :  request.form.get('email')
            },{'$set' : {
                'email'  : request.form.get('email'),
                'name' : request.form.get('name'),
                'phone' : request.form.get('phone'),
                'date'  : request.form.get('date'),
                
               }
                
            }
            )
            global user_activo
            user_activo = request.form.get('email')
    
    return redirect('cuenta')

@app.route('/cerrar')
def cerrar():
    global user_activo
    user_activo = ""
    session['logged_in'] = None
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
        if validacion:
            return render_template('registro.html', validacion= validacion)

        # Verificar si el usuario ya existe en la base de datos
        if db.db.usuarios.find_one({'email': date['email']}):
            return render_template('registro.html', validacion= "Usuario ya registrado")

        # Cifrar la contraseña antes de almacenarla en la base de datos
            # Encrypt the password
        date['password'] = pbkdf2_sha256.encrypt(date['password'])

        # Add your database logic or other actions here

        # Insertar el usuario en la base de datos
        validacion = validateTar(date)
        if validacion:
            return render_template('registro.html', validacion= validacion)

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
        
        session['logged_in'] = True
        return redirect(url_for('menu'))


    return render_template('registro.html', validacion = None)

@app.route('/menu', methods=['GET', 'POST'])
@login_require
def menu():
    return render_template('dashboard.html')

@app.route('/inicio', methods=['POST', 'GET'])
def inicio():
    if request.method == 'POST':
        correo = request.form.get('email')
        

        
        user = db.db.usuarios.find_one({
        "email": request.form.get('email')
        })
    
        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            global user_activo 
            user_activo= correo
            session['logged_in'] = True
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

def validateTar(customer):
    print(customer)
    error_message = None
    
    # Validar Usuario
    if not customer['nameT']:
        error_message = "Please Enter your Name !!"
    elif not customer['number']:
        error_message = 'Enter your Tarjet Number'
    elif len (customer['number']) < 16:
        error_message = 'Tarjet Number must be 16 char Long'
    elif not customer['fecha']:
        error_message  = 'No valida'
    elif len (customer['ccv']) < 3:
        error_message = 'CCV no valido'
    # saving
    return error_message


if __name__ == '__main__':
    app.run(debug=True)
