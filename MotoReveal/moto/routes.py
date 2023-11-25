from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from functools import wraps
import string
from passlib.hash import pbkdf2_sha256
from app import app, db



@app.route('/moto/agregar',methods=['POST'])
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