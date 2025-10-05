from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, current_user

from app.models import User
from app.database import db

auth = Blueprint('auth', __name__)

# LOGIN
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Collect the username, password from the Login form
    if request.method=='POST':

        username = request.json.get('username', None)
        password = request.json.get('password', None)

        _user = User.query.filter_by(username=username).first()

        # Validating the user
        if not _user or not _user.check_password(password):
            return jsonify({"message":"Wrong username or password"}), 401

        access_token = create_access_token(identity=_user)

        return jsonify(access_token=access_token)

    return jsonify(message='Login Page')


# REGISTER - Public access for patients to register themselves
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':

        try:
            
            username = request.json.get('username', None)
            first_name = request.json.get('first_name', None)
            last_name = request.json.get('last_name', None)

            email = request.json.get('email', None)
            password = request.json.get('password', None)
            retype_password = request.json.get('retype_password', None)

            user = User.query.filter_by(username=username).first()

            if not user:
                if password != retype_password:
                    return jsonify(message='Passwords do not match!'), 400

                new_user = User(username=username, email=email,
                                first_name=first_name, last_name=last_name, role='patient')
                    
                new_user.set_password(password)
                
                db.session.add(new_user)
                db.session.commit()
                
                return jsonify(message='Patient created!'), 201
                
            else:
                return jsonify(message='Patient already exists'), 400
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error creating patient: {str(e)}"}), 500       
        
    return jsonify(message='Registration Page')