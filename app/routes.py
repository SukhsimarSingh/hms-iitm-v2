from app import app
from functools import wraps

from flask import render_template, request, jsonify, flash
from flask_jwt_extended import create_access_token, jwt_required, current_user

from app.models import User
from app.database import db
from datetime import datetime

# RBA
def roles_required(required_role):
    def wrapper(func):
        @wraps(func)
        @jwt_required()
        def decorator(*args, **kwargs):
            if current_user.role!=required_role:
                return jsonify(message = "Access denined - insufficient role"), 403
            return func(*args, **kwargs)
        return decorator
    return wrapper

# HOME
@app.route('/')
def home():
    return render_template('home.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Collect the username, password from the Login form
    if request.method=='POST':

        username = request.json.get('username', None)
        password = request.json.get('password', None)

        user = User.query.filter_by(username=username).one_or_none()

        # Validating the user
        if not user or not user.check_password(password):
            return jsonify("Wrong username or password"), 401

        access_token = create_access_token(identity=user)

        return jsonify(access_token=access_token)

    # Let the user log in
    return render_template('login.html')

# REGISTER - Public access for patients to register themselves
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':

        try:
            username = request.json.get('username', None)
            first_name = request.json.get('first_name', None)
            last_name = request.json.get('last_name', None)

            email = request.json.get('email', None)
            password = request.json.get('password', None)
            retype_password = request.json.get('retype_password', None)

            user = User.query.filter_by(username=username).one_or_none()

            if not user:
                if password!=retype_password:
                    flash('Passwords not matching!')

                new_user = User(username=username, email=email,
                            confirmed_at=datetime.now(), first_name=first_name, last_name=last_name, role='patient')
                    
                new_user.set_password(password)
                
                db.session.add(new_user)
                db.session.commit()
                
                return jsonify(message='User created!')
        
        except Exception as e:
            return e    
        
        return jsonify(message='User already exists')
        
    return "Register Page"

# DASHBOARD
@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    return jsonify(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        current_user=current_user.last_name
    )

# ADMIN
@app.route('/admin', methods=['GET', 'POST'])
@roles_required("admin")
def admin():
    return "Admins allowed"