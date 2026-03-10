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


# UPDATE DOCTOR
@views.route('/api/update/doctor/<int:doctor_id>', methods=['PUT', 'PATCH'])
@roles_required('admin')
def update_doctor(doctor_id):
    """Update doctor and associated user details"""
    
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        return jsonify({"message": "Doctor not found!"}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    try:
        # Update doctor-specific fields
        if 'specialization' in data:
            doctor.specialization = data['specialization']
        
        if 'department' in data:
            doctor.department = data['department']
        
        if 'experience' in data:
            doctor.experience = data['experience']
        
        if 'availability' in data:
            doctor.availability = data['availability']
        
        # Update associated user fields
        user = User.query.get(doctor.user_id)
        
        if user:
            if 'first_name' in data:
                user.first_name = data['first_name']
                # Update doctor name as well
                last_name = data.get('last_name', user.last_name)
                doctor.name = f"{data['first_name']} {last_name}"
            
            if 'last_name' in data:
                user.last_name = data['last_name']
                # Update doctor name as well
                first_name = data.get('first_name', user.first_name)
                doctor.name = f"{first_name} {data['last_name']}"
            
            if 'email' in data:
                # Check if email already exists for another user
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != user.id:
                    return jsonify({"message": "Email already in use"}), 409
                user.email = data['email']
            
            if 'username' in data:
                # Check if username already exists for another user
                existing_user = User.query.filter_by(username=data['username']).first()
                if existing_user and existing_user.id != user.id:
                    return jsonify({"message": "Username already in use"}), 409
                user.username = data['username']
            
            if 'password' in data:
                user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            "message": "Doctor updated successfully!",
            "doctor_id": doctor.id,
            "doctor_details": {
                "name": doctor.name,
                "specialization": doctor.specialization,
                "department": doctor.department,
                "experience": doctor.experience,
                "availability": doctor.availability
            },
            "user_details": {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating doctor: {str(e)}"}), 500


# UPDATE PATIENT
@views.route('/api/update/patient/<int:patient_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_patient(patient_id):
    """Update patient details - patients can update their own, admins can update any"""
    
    patient = User.query.filter_by(id=patient_id, role='patient').first()
    
    if not patient:
        return jsonify({"message": "Patient not found!"}), 404
    
    # Check authorization - patients can only update their own profile
    if current_user.role != 'admin' and current_user.id != patient_id:
        return jsonify({"message": "Access denied - You can only update your own profile"}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    try:
        # Update user fields
        if 'first_name' in data:
            patient.first_name = data['first_name']
        
        if 'last_name' in data:
            patient.last_name = data['last_name']
        
        if 'email' in data:
            # Check if email already exists for another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != patient.id:
                return jsonify({"message": "Email already in use"}), 409
            patient.email = data['email']
        
        if 'username' in data:
            # Check if username already exists for another user
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != patient.id:
                return jsonify({"message": "Username already in use"}), 409
            patient.username = data['username']
        
        if 'password' in data:
            patient.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            "message": "Patient updated successfully!",
            "patient_id": patient.id,
            "patient_details": {
                "username": patient.username,
                "email": patient.email,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "role": patient.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating patient: {str(e)}"}), 500


# REMOVE DOCTOR
@views.route('/api/remove/doctor', methods=['DELETE', 'POST'])
@roles_required('admin')
def remove_doctor():
    
    if request.method in ['POST', 'DELETE']:
        
        doctor_id = request.json.get('doctor_id', None)

        if not doctor_id:
            return jsonify({"message": "Doctor ID is required"}), 400

        doctor = Doctor.query.get(doctor_id)

        if not doctor:
            return jsonify({"message": "Doctor not found!"}), 404

        try:
            # Get the associated user before deleting doctor
            user = User.query.get(doctor.user_id)
            
            # Delete doctor record first (due to foreign key)
            db.session.delete(doctor)
            
            # Delete associated user account if exists
            if user:
                db.session.delete(user)
            
            db.session.commit()

            return jsonify({
                "message": "Doctor and associated user removed successfully!",
                "doctor_id": doctor_id
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error removing doctor: {str(e)}"}), 500
    
    return jsonify({"message": "Remove Doctor Page"})

# REMOVE PATIENT
@views.route('/api/remove/patient', methods=['DELETE', 'POST'])
@roles_required('admin')
def remove_patient():
    
    if request.method in ['POST', 'DELETE']:
        
        patient_id = request.json.get('patient_id', None)

        if not patient_id:
            return jsonify({"message": "Patient ID is required"}), 400

        patient = User.query.filter_by(id=patient_id, role='patient').first()

        if not patient:
            return jsonify({"message": "Patient not found!"}), 404

        try:
            db.session.delete(patient)
            db.session.commit()

            return jsonify({
                "message": "Patient removed successfully!",
                "patient_id": patient_id
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error removing patient: {str(e)}"}), 500

    return jsonify({"message": "Remove Patient Page"})


# BLACKLIST/BAN DOCTOR
@views.route('/api/blacklist/doctor/<int:doctor_id>', methods=['POST', 'PATCH'])
@roles_required('admin')
def blacklist_doctor(doctor_id):
    """Blacklist/ban a doctor (deactivate account)"""
    
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        return jsonify({"message": "Doctor not found!"}), 404
    
    user = User.query.get(doctor.user_id)
    
    if not user:
        return jsonify({"message": "Associated user not found!"}), 404
    
    try:
        # Toggle active status or set based on request
        data = request.get_json() or {}
        
        if 'active' in data:
            user.active = data['active']
        else:
            # Toggle if no specific value provided
            user.active = not user.active
        
        db.session.commit()
        
        status = "activated" if user.active else "blacklisted"
        
        return jsonify({
            "message": f"Doctor {status} successfully!",
            "doctor_id": doctor_id,
            "user_id": user.id,
            "active": user.active,
            "doctor_details": {
                "name": doctor.name,
                "email": user.email,
                "username": user.username
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating doctor status: {str(e)}"}), 500


# BLACKLIST/BAN PATIENT
@views.route('/api/blacklist/patient/<int:patient_id>', methods=['POST', 'PATCH'])
@roles_required('admin')
def blacklist_patient(patient_id):
    """Blacklist/ban a patient (deactivate account)"""
    
    patient = User.query.filter_by(id=patient_id, role='patient').first()
    
    if not patient:
        return jsonify({"message": "Patient not found!"}), 404
    
    try:
        # Toggle active status or set based on request
        data = request.get_json() or {}
        
        if 'active' in data:
            patient.active = data['active']
        else:
            # Toggle if no specific value provided
            patient.active = not patient.active
        
        db.session.commit()
        
        status = "activated" if patient.active else "blacklisted"
        
        return jsonify({
            "message": f"Patient {status} successfully!",
            "patient_id": patient_id,
            "active": patient.active,
            "patient_details": {
                "username": patient.username,
                "email": patient.email,
                "first_name": patient.first_name,
                "last_name": patient.last_name
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating patient status: {str(e)}"}), 500


# GET BLACKLISTED USERS
@views.route('/api/blacklist/list', methods=['GET'])
@roles_required('admin')
def get_blacklisted_users():
    """Get all blacklisted (inactive) users"""
    
    try:
        # Get all inactive users
        inactive_users = User.query.filter_by(active=False).all()
        
        blacklist = []
        
        for user in inactive_users:
            user_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "active": user.active
            }
            
            # Add doctor-specific info if applicable
            if user.role == 'doctor' and user.doctor:
                user_info["doctor_details"] = {
                    "doctor_id": user.doctor.id,
                    "name": user.doctor.name,
                    "specialization": user.doctor.specialization,
                    "department": user.doctor.department
                }
            
            blacklist.append(user_info)
        
        return jsonify({
            "message": "Blacklisted users retrieved successfully",
            "count": len(blacklist),
            "blacklisted_users": blacklist
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error retrieving blacklisted users: {str(e)}"}), 500


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