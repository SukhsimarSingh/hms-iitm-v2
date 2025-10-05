from app import app

from flask import render_template, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, current_user

from app.models import User

# HOME PAGE
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Collect the username, password from the Login form
    if request.method=='POST':
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        user = User.query.filter_by(email=email).one_or_none()
        # Validating the user
        if not user or not user.check_password(password):
            return jsonify("Wrong username or password"), 401

        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token)

    # Let the user log in
    return render_template('login.html')


# USER DASHBOARD
@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    # current_user = get_jwt_identity()
    # return jsonify(logged_in_as=current_user), 200
    return jsonify(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        current_user=current_user.last_name
    )


# ADMIN PAGE
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return "Admin"