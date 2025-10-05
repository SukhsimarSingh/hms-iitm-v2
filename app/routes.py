from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, current_user

from app.models import User, Doctor
from app.database import db
from app.security import roles_required

views = Blueprint('views', __name__)

# HOME
@views.route('/')
@views.route('/home')
def home():
    # return render_template('home.html')
    return jsonify(message='Home Page')

# GET PATIENTS / DOCTORS
@views.route('/api/get/<string:role>', methods=['GET'])
@jwt_required()
def get_users(role):
    
    if role in ['patient', 'doctor']:
        users = User.query.filter_by(role=role).all()

        users_list = []

        for user in users:
            info = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "email": user.email
            }
            
            # If it's a doctor, include doctor-specific details
            if role == 'doctor' and user.doctor:
                info["doctor_details"] = {
                    "doctor_id": user.doctor.id,
                    "specialization": user.doctor.specialization,
                    "experience": user.doctor.experience
                }

            users_list.append(info)

        return jsonify(users_list)
    
    return jsonify({"message": "Role not applicable"})


# GET DOCTOR? PATIENT DETAILS WITH USER INFO
@views.route('/api/get/<string:role>/<string:username>', methods=['GET'])
@jwt_required()
def get_details(role, username):
    try:
        user=User.query.filter_by(username=username, role=role).first()

        if not user:
            return jsonify({"message": "User not found"}), 404

        if role=='doctor':
            doc_info = user.doctor           
            return jsonify({
                "doctor_id": doc_info.id,
                "name": doc_info.name,
                "specialization": doc_info.specialization,
                "experience": doc_info.experience,
                "user_details": {
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role
                }
            })
        
        elif role=='patient':
            return jsonify({"user_details": {
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role
                }
            })
        
        return jsonify({"message": "User not Patient or Doctor"}), 404
        
    except Exception as e:
        return jsonify({"message": f"Error fetching doctor: {str(e)}"}), 500


# ADD DOCTOR
@views.route('/api/add/doctor', methods=['GET', 'POST'])
@roles_required('admin')
def add_doctor():
    
    if request.method=='POST':
        
        # Gerate a Random UUID as username for Doctor
        username = request.json.get('username', None)
        first_name = request.json.get('first_name', None)
        last_name = request.json.get('last_name', None)
        email = request.json.get('email', None)

        # Doctor specific fields
        specialization = request.json.get('specialization', None)
        department = request.json.get('department', None)
        experience = request.json.get('experience', None)

        doctor = User.query.filter_by(email=email, role='doctor').first()

        if not doctor:
            try:
                name = first_name + " " + last_name
                
                _user = User(username=username, first_name=first_name, last_name=last_name, email=email, role='doctor')
                _user.set_password(username)
                
                db.session.add(_user)
                db.session.flush()

                _doctor = Doctor(name=name, specialization=specialization, department=department, experience=experience, user_id=_user.id)
                
                db.session.add(_doctor)
                db.session.commit()

                return jsonify({
                    "message": "Doctor Added!",
                    "doctor_id": _doctor.id,
                    "user_id": _user.id,
                    "username": username}), 201
                
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": f"Error creating doctor: {str(e)}"}), 500

        return jsonify({"message": "Doctor already exists!"}), 400
    
    return jsonify({"message": "Add Doctor Page"})


# ADMIN
@views.route('/admin', methods=['GET', 'POST'])
@roles_required("admin")
def admin():
    return jsonify(message='Admin Page')


# DASHBOARD
@views.route('/api/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    return jsonify(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name
    )