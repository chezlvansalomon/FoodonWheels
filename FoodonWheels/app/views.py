
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask import Flask, render_template, redirect, url_for, request, Response, flash, jsonify, send_file, send_from_directory, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.orm import sessionmaker
from werkzeug.exceptions import abort
from passlib.hash import sha256_crypt
from sqlalchemy import create_engine
from models import DBconn, User
from sqlalchemy.orm import exc
from datetime import datetime
from app import app, db
from forms import *
import hashlib
import sys, os

login_manager = LoginManager()
login_manager.init_app(app)
key = "1290gath43quz1@"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def spcall(qry, param, commit=False):
    """ Function which communicates with the database """

    try:
        dbo = DBconn()
        cursor = dbo.getcursor()
        cursor.callproc(qry, param)
        res = cursor.fetchall()
        if commit:
            dbo.dbcommit()
        return res
    except:
        res = [('Error: ' + str(sys.exc_info()[0]) + ' '
               + str(sys.exc_info()[1]), )]
    return res


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    """ The homepage """

    return send_from_directory(os.path.join(APP_ROOT, 'static', 'html'), 'index.html')

    

@app.errorhandler(404)
def page_not_found(e):
	""" 404 Page Not Found Handler """

	return jsonify({'status': '404', 'message': 'Sorry, the page you are looking for was not found'})


@app.errorhandler(500)
def internal_server_error(e):
    """ 500 Internal Server Error """

    return jsonify({'status': '500', 'message': 'Internal Server Error'})


@app.route('/')
@app.route('/index')
def index():
	return send_file("templates/index.html")


@app.route('/api/registeruser', methods=['POST'])
def register():
    """ User registration function """

    passw = request.form["password"]
    passw = passw + key
    passw = hashlib.md5(passw.encode())
    passw = passw.hexdigest()
    email = request.form["email"]


    if 'Error' in str(res[0][0]):
        return jsonify({'status': 'error', 'message': res[0][0]})
    return jsonify({'status': 'ok', 'message': res[0][0]})


@app.route('/api/loginuser', methods=['POST'])
def login():
    """ User login function """

    attempted_email = request.form["email"]
    attempted_password = request.form["password"]
    attempted_password = attempted_password + key
    
    attempted_password = hashlib.md5(attempted_password.encode())
    attempted_password = attempted_password.hexdigest()
    
    res = spcall('list_users', ())
    error = True
    
    for element in res:
        # email element[4]
        # password element[5]
        if attempted_email == element[3]:
            userinfo = {'firstname': element[0], 'lastname': element[1], 'middle_initial': element[2], 
            'email': element[3], 'token':hashlib.md5( str(element[0] + element[4] ).encode()).hexdigest()}
            user = User(element[0], element[1], element[2], element[3], element[4])
            stored_password = element[4] # attempted_password should match this
            error = False
                  
    
    if error == True:
        return jsonify({'status': 'error', 'message': 'email does not exist'})
    if (attempted_password == stored_password):
        return jsonify({'status': 'Successful', 'User_Information': userinfo,'message': 'Logged in successfully!'})
    else:
        return jsonify({'status': 'error', 'message': 'password or email is incorrect'})


@app.route('/api/logout')
def logout():
    """ User logout function """
    return jsonify({'status':'ok','message':'logged out'})
