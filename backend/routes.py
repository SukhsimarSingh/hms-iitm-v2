from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, current_user

from backend.models import User, Doctor, Patient, Appointment
from backend.database import db
from backend.security import roles_required

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
                "email": user.email,
                "active": user.active
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
                    "role": user.role,
                    "active": user.active
                }
            })
        
        elif role=='patient':
            return jsonify({"user_details": {
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "active": user.active
                }
            })
        
        return jsonify({"message": "User not Patient or Doctor"}), 404
        
    except Exception as e:
        return jsonify({"message": f"Error fetching user: {str(e)}"}), 500


# ADD DOCTOR
@views.route('/api/add/doctor', methods=['GET', 'POST'])
@roles_required('admin')
def add_doctor():
    
    if request.method=='POST':
        
        # Get required fields
        username = request.json.get('username', None)
        first_name = request.json.get('first_name', None)
        last_name = request.json.get('last_name', None)
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        # Doctor specific fields
        specialization = request.json.get('specialization', None)
        department = request.json.get('department', None)
        experience = request.json.get('experience', None)
        
        # Validate required fields
        if not all([username, first_name, last_name, password, email, specialization, department]):
            return jsonify({"message": "Missing required fields"}), 400

        doctor = User.query.filter_by(email=email, role='doctor').first()

        if not doctor:
            try:
                name = first_name + " " + last_name
                
                _user = User(username=username, first_name=first_name, last_name=last_name, email=email, role='doctor')
                _user.set_password(password)
                
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


# ADMIN DASHBOARD
@views.route('/api/admin/dashboard', methods=['GET'])
@roles_required("admin")
def admin_dashboard():
    """Get comprehensive admin dashboard data"""
    
    try:
        # Get all doctors with their details
        doctors = User.query.filter_by(role='doctor').all()
        doctors_list = []
        
        for user in doctors:
            doctor_info = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "active": user.active,
                "confirmed_at": user.confirmed_at.isoformat() if user.confirmed_at else None
            }
            
            if user.doctor:
                doctor_info["doctor_id"] = user.doctor.id
                doctor_info["name"] = user.doctor.name
                doctor_info["specialization"] = user.doctor.specialization
                doctor_info["department"] = user.doctor.department
                doctor_info["experience"] = user.doctor.experience
                doctor_info["availability"] = user.doctor.availability
            
            doctors_list.append(doctor_info)
        
        # Get all patients with their details
        patients = User.query.filter_by(role='patient').all()
        patients_list = []
        
        for user in patients:
            patient_info = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "active": user.active,
                "confirmed_at": user.confirmed_at.isoformat() if user.confirmed_at else None
            }
            
            patients_list.append(patient_info)
        
        # Get upcoming appointments
        appointments = Appointment.query.all()
        appointments_list = []
        
        for appointment in appointments:
            # Get patient and doctor details
            patient = User.query.join(Patient).filter(Patient.id == appointment.patient_id).first()
            doctor = Doctor.query.get(appointment.doctor_id)
            
            appointment_info = {
                "id": appointment.id,
                "date": appointment.date.isoformat() if appointment.date else None,
                "time": appointment.time.isoformat() if appointment.time else None,
                "status": appointment.status,
                "patient_id": appointment.patient_id,
                "doctor_id": appointment.doctor_id,
                "patient": {
                    "id": patient.id if patient else None,
                    "name": f"{patient.first_name} {patient.last_name}" if patient else "N/A",
                    "username": patient.username if patient else None
                },
                "doctor": {
                    "id": doctor.id if doctor else None,
                    "name": doctor.name if doctor else "N/A",
                    "specialization": doctor.specialization if doctor else None,
                    "department": doctor.department if doctor else None
                }
            }
            
            appointments_list.append(appointment_info)
        
        # Get statistics
        stats = {
            "total_doctors": len(doctors_list),
            "active_doctors": len([d for d in doctors_list if d['active']]),
            "blacklisted_doctors": len([d for d in doctors_list if not d['active']]),
            "total_patients": len(patients_list),
            "active_patients": len([p for p in patients_list if p['active']]),
            "blacklisted_patients": len([p for p in patients_list if not p['active']]),
            "total_appointments": len(appointments_list),
            "pending_appointments": len([a for a in appointments_list if a['status'] == 'Pending']),
            "completed_appointments": len([a for a in appointments_list if a['status'] == 'Completed']),
            "cancelled_appointments": len([a for a in appointments_list if a['status'] == 'Cancelled'])
        }
        
        return jsonify({
            "message": "Admin dashboard data retrieved successfully",
            "admin": {
                "username": current_user.username,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name
            },
            "statistics": stats,
            "registered_doctors": doctors_list,
            "registered_patients": patients_list,
            "upcoming_appointments": appointments_list
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error retrieving admin dashboard: {str(e)}"}), 500


# DOCTOR DASHBOARD
@views.route('/api/doctor/dashboard', methods=['GET'])
@roles_required('doctor')
def doctor_dashboard():
    """Get comprehensive doctor dashboard data"""
    
    try:
        # Get doctor record
        doctor = current_user.doctor
        
        if not doctor:
            return jsonify({"message": "Doctor profile not found"}), 404
        
        # Get doctor's upcoming appointments
        upcoming_appointments = Appointment.query.filter_by(
            doctor_id=doctor.id
        ).all()
        
        appointments_list = []
        for appointment in upcoming_appointments:
            # Get patient details
            patient_record = Patient.query.get(appointment.patient_id)
            patient_user = User.query.get(patient_record.user_id) if patient_record else None
            
            # Skip blacklisted patients
            if patient_user and not patient_user.active:
                continue
            
            appointment_info = {
                "id": appointment.id,
                "date": appointment.date.isoformat() if appointment.date else None,
                "time": appointment.time.isoformat() if appointment.time else None,
                "status": appointment.status,
                "patient": {
                    "id": patient_record.id if patient_record else None,
                    "name": patient_record.name if patient_record else "N/A",
                    "age": patient_record.age if patient_record else None,
                    "contact": patient_record.contact if patient_record else None,
                    "username": patient_user.username if patient_user else None,
                    "email": patient_user.email if patient_user else None
                }
            }
            
            # Add treatment info if exists
            if appointment.treatment:
                appointment_info["treatment"] = {
                    "id": appointment.treatment.id,
                    "diagnosis": appointment.treatment.diagnosis,
                    "prescription": appointment.treatment.prescription,
                    "notes": appointment.treatment.notes
                }
            
            appointments_list.append(appointment_info)
        
        # Get patient history (all patients this doctor has seen)
        all_appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
        patient_ids = list(set([apt.patient_id for apt in all_appointments]))
        
        patient_history = []
        for patient_id in patient_ids:
            patient_record = Patient.query.get(patient_id)
            if patient_record:
                patient_user = User.query.get(patient_record.user_id)
                
                # Skip blacklisted patients
                if patient_user and not patient_user.active:
                    continue
                
                # Count appointments for this patient
                patient_appointments = [a for a in all_appointments if a.patient_id == patient_id]
                
                patient_info = {
                    "patient_id": patient_record.id,
                    "name": patient_record.name,
                    "age": patient_record.age,
                    "contact": patient_record.contact,
                    "username": patient_user.username if patient_user else None,
                    "email": patient_user.email if patient_user else None,
                    "total_appointments": len(patient_appointments),
                    "last_visit": max([a.date for a in patient_appointments if a.date]).isoformat() if patient_appointments else None
                }
                
                patient_history.append(patient_info)
        
        # Statistics
        stats = {
            "total_appointments": len(all_appointments),
            "upcoming_appointments": len([a for a in appointments_list if a['status'] == 'Pending']),
            "completed_appointments": len([a for a in all_appointments if a.status == 'Completed']),
            "total_patients": len(patient_history)
        }
        
        return jsonify({
            "message": "Doctor dashboard data retrieved successfully",
            "doctor": {
                "user_id": current_user.id,
                "doctor_id": doctor.id,
                "username": current_user.username,
                "email": current_user.email,
                "name": doctor.name,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "specialization": doctor.specialization,
                "department": doctor.department,
                "experience": doctor.experience,
                "availability": doctor.availability
            },
            "statistics": stats,
            "upcoming_appointments": appointments_list,
            "patient_history": patient_history
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error retrieving doctor dashboard: {str(e)}"}), 500


# UPDATE AVAILABILITY
@views.route('/api/doctor/availability', methods=['PUT', 'PATCH'])
@roles_required('doctor')
def update_availability():
    """Update doctor availability status"""
    
    doctor = current_user.doctor
    
    if not doctor:
        return jsonify({"message": "Doctor profile not found"}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    if 'availability' not in data:
        return jsonify({"message": "Availability field is required"}), 400
    
    # Validate availability status
    allowed_statuses = ['Available', 'Busy', 'On Leave', 'Not Available']
    new_availability = data['availability']
    
    if new_availability not in allowed_statuses:
        return jsonify({
            "message": "Invalid availability status",
            "allowed_values": allowed_statuses
        }), 400
    
    try:
        doctor.availability = new_availability
        db.session.commit()
        
        return jsonify({
            "message": "Availability updated successfully!",
            "doctor": {
                "doctor_id": doctor.id,
                "name": doctor.name,
                "availability": doctor.availability,
                "specialization": doctor.specialization,
                "department_id": doctor.department_id
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating availability: {str(e)}"}), 500


# PATIENT DASHBOARD
@views.route('/api/patient/dashboard', methods=['GET'])
@roles_required('patient')
def patient_dashboard():
    """Get comprehensive patient dashboard data"""
    
    try:
        # Get patient record (if exists)
        patient_record = Patient.query.filter_by(user_id=current_user.id).first()
        
        # Get patient's appointments
        appointments_list = []
        
        if patient_record:
            appointments = Appointment.query.filter_by(
                patient_id=patient_record.id
            ).all()
            
            for appointment in appointments:
                # Get doctor details
                doctor = Doctor.query.get(appointment.doctor_id)
                doctor_user = User.query.get(doctor.user_id) if doctor else None
                
                appointment_info = {
                    "id": appointment.id,
                    "date": appointment.date.isoformat() if appointment.date else None,
                    "time": appointment.time.isoformat() if appointment.time else None,
                    "status": appointment.status,
                    "doctor": {
                        "id": doctor.id if doctor else None,
                        "name": doctor.name if doctor else "N/A",
                        "specialization": doctor.specialization if doctor else None,
                        "department": doctor.department if doctor else None,
                        "experience": doctor.experience if doctor else None,
                        "username": doctor_user.username if doctor_user else None,
                        "email": doctor_user.email if doctor_user else None
                    }
                }
                
                # Add treatment info if exists
                if appointment.treatment:
                    appointment_info["treatment"] = {
                        "id": appointment.treatment.id,
                        "diagnosis": appointment.treatment.diagnosis,
                        "prescription": appointment.treatment.prescription,
                        "notes": appointment.treatment.notes
                    }
                    
                    # Add medicines if exist
                    if appointment.treatment.medicine:
                        medicines = []
                        for medicine in appointment.treatment.medicine:
                            medicines.append({
                                "id": medicine.id,
                                "name": medicine.name,
                                "description": medicine.description
                            })
                        appointment_info["treatment"]["medicines"] = medicines
                
                appointments_list.append(appointment_info)
        
        # Get all available departments (for booking appointments)
        all_doctors = Doctor.query.all()
        departments = list(set([d.department for d in all_doctors if d.department]))
        
        # Get available doctors by department
        doctors_by_department = {}
        for dept in departments:
            dept_doctors = Doctor.query.filter_by(department=dept).all()
            doctors_by_department[dept] = []
            
            for doctor in dept_doctors:
                doctor_user = User.query.get(doctor.user_id)
                if doctor_user and doctor_user.active:
                    doctors_by_department[dept].append({
                        "doctor_id": doctor.id,
                        "name": doctor.name,
                        "specialization": doctor.specialization,
                        "experience": doctor.experience,
                        "availability": doctor.availability
                    })
        
        # Statistics
        stats = {
            "total_appointments": len(appointments_list),
            "upcoming_appointments": len([a for a in appointments_list if a['status'] == 'Pending']),
            "completed_appointments": len([a for a in appointments_list if a['status'] == 'Completed']),
            "cancelled_appointments": len([a for a in appointments_list if a['status'] == 'Cancelled'])
        }
        
        return jsonify({
            "message": "Patient dashboard data retrieved successfully",
            "patient": {
                "user_id": current_user.id,
                "patient_id": patient_record.id if patient_record else None,
                "username": current_user.username,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "name": patient_record.name if patient_record else f"{current_user.first_name} {current_user.last_name}",
                "age": patient_record.age if patient_record else None,
                "contact": patient_record.contact if patient_record else None
            },
            "statistics": stats,
            "upcoming_appointments": appointments_list,
            "departments": departments,
            "doctors_by_department": doctors_by_department
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error retrieving patient dashboard: {str(e)}"}), 500


# CREATE/BOOK APPOINTMENT
@views.route('/api/appointment/create', methods=['POST'])
@jwt_required()
def create_appointment():
    """Create a new appointment - patients or admins can create"""
    
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    # Required fields
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    date = data.get('date')
    time = data.get('time')
    
    if not all([patient_id, doctor_id, date, time]):
        return jsonify({"message": "Missing required fields (patient_id, doctor_id, date, time)"}), 400
    
    # Verify patient exists
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404
    
    # Verify doctor exists and is active
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404
    
    doctor_user = User.query.get(doctor.user_id)
    if not doctor_user or not doctor_user.active:
        return jsonify({"message": "Doctor is not available"}), 400
    
    # Check authorization - patients can only book for themselves
    if current_user.role == 'patient':
        if patient.user_id != current_user.id:
            return jsonify({"message": "You can only book appointments for yourself"}), 403
    
    try:
        from datetime import datetime as dt, time as time_obj
        
        # Parse date and time
        if isinstance(date, str):
            appointment_date = dt.fromisoformat(date).date()
        else:
            appointment_date = date
            
        if isinstance(time, str):
            # Parse time string (HH:MM:SS or HH:MM format)
            if 'T' in time:
                appointment_time = dt.fromisoformat(time).time()
            else:
                # Handle time-only format
                parts = time.split(':')
                appointment_time = time_obj(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
        else:
            appointment_time = time
        
        # CONFLICT PREVENTION: Check for double booking
        # Check if doctor already has an appointment at this date and time
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_date,
            time=appointment_time
        ).filter(
            Appointment.status.in_(['Pending', 'Confirmed'])
        ).first()
        
        if existing_appointment:
            return jsonify({
                "message": "Doctor is not available at this time slot. Please choose another time.",
                "conflict": {
                    "appointment_id": existing_appointment.id,
                    "date": existing_appointment.date.isoformat(),
                    "time": existing_appointment.time.isoformat(),
                    "status": existing_appointment.status
                }
            }), 409
        
        # Check if patient already has an appointment at this time
        patient_conflict = Appointment.query.filter_by(
            patient_id=patient_id,
            date=appointment_date,
            time=appointment_time
        ).filter(
            Appointment.status.in_(['Pending', 'Confirmed'])
        ).first()
        
        if patient_conflict:
            return jsonify({
                "message": "You already have an appointment at this time slot.",
                "conflict": {
                    "appointment_id": patient_conflict.id,
                    "date": patient_conflict.date.isoformat(),
                    "time": patient_conflict.time.isoformat(),
                    "doctor_id": patient_conflict.doctor_id
                }
            }), 409
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            date=appointment_date,
            time=appointment_time,
            status='Pending'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            "message": "Appointment created successfully!",
            "appointment": {
                "id": appointment.id,
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "date": appointment.date.isoformat(),
                "time": appointment.time.isoformat(),
                "status": appointment.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating appointment: {str(e)}"}), 500


# UPDATE APPOINTMENT
@views.route('/api/appointment/update/<int:appointment_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_appointment(appointment_id):
    """Update appointment - change date, time, or status"""
    
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    # Check authorization
    patient = Patient.query.get(appointment.patient_id)
    if current_user.role == 'patient' and patient.user_id != current_user.id:
        return jsonify({"message": "You can only update your own appointments"}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    try:
        from datetime import datetime as dt
        
        # Store new date/time for conflict checking
        new_date = None
        new_time = None
        
        # Update fields
        if 'date' in data:
            new_date = dt.fromisoformat(data['date']).date() if isinstance(data['date'], str) else data['date']
        
        if 'time' in data:
            new_time = dt.fromisoformat(data['time']).time() if isinstance(data['time'], str) else data['time']
        
        # CONFLICT PREVENTION: Check for conflicts if date or time is being changed
        if new_date or new_time:
            check_date = new_date if new_date else appointment.date
            check_time = new_time if new_time else appointment.time
            
            # Check if doctor has another appointment at the new time
            conflict = Appointment.query.filter_by(
                doctor_id=appointment.doctor_id,
                date=check_date,
                time=check_time
            ).filter(
                Appointment.id != appointment_id,  # Exclude current appointment
                Appointment.status.in_(['Pending', 'Confirmed'])
            ).first()
            
            if conflict:
                return jsonify({
                    "message": "Doctor is not available at this time slot. Please choose another time.",
                    "conflict": {
                        "appointment_id": conflict.id,
                        "date": conflict.date.isoformat(),
                        "time": conflict.time.isoformat()
                    }
                }), 409
            
            # Update the fields
            if new_date:
                appointment.date = new_date
            if new_time:
                appointment.time = new_time
        
        if 'status' in data:
            # Only doctors and admins can change status
            if current_user.role in ['doctor', 'admin']:
                # Validate status
                valid_statuses = ['Pending', 'Confirmed', 'Completed', 'Cancelled']
                if data['status'] not in valid_statuses:
                    return jsonify({
                        "message": "Invalid status",
                        "allowed_values": valid_statuses
                    }), 400
                appointment.status = data['status']
            else:
                return jsonify({"message": "Only doctors and admins can change appointment status"}), 403
        
        db.session.commit()
        
        return jsonify({
            "message": "Appointment updated successfully!",
            "appointment": {
                "id": appointment.id,
                "date": appointment.date.isoformat(),
                "time": appointment.time.isoformat(),
                "status": appointment.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating appointment: {str(e)}"}), 500


# CANCEL APPOINTMENT
@views.route('/api/appointment/cancel/<int:appointment_id>', methods=['POST', 'PATCH'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    # Check authorization
    patient = Patient.query.get(appointment.patient_id)
    doctor = Doctor.query.get(appointment.doctor_id)
    
    # Patients can cancel their own, doctors can cancel theirs, admins can cancel any
    authorized = False
    if current_user.role == 'admin':
        authorized = True
    elif current_user.role == 'patient' and patient.user_id == current_user.id:
        authorized = True
    elif current_user.role == 'doctor' and doctor.user_id == current_user.id:
        authorized = True
    
    if not authorized:
        return jsonify({"message": "You are not authorized to cancel this appointment"}), 403
    
    try:
        appointment.status = 'Cancelled'
        db.session.commit()
        
        return jsonify({
            "message": "Appointment cancelled successfully!",
            "appointment_id": appointment_id,
            "status": appointment.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error cancelling appointment: {str(e)}"}), 500


# DELETE APPOINTMENT
@views.route('/api/appointment/delete/<int:appointment_id>', methods=['DELETE'])
@roles_required('admin')
def delete_appointment(appointment_id):
    """Permanently delete an appointment (admin only)"""
    
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    try:
        db.session.delete(appointment)
        db.session.commit()
        
        return jsonify({
            "message": "Appointment deleted successfully!",
            "appointment_id": appointment_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting appointment: {str(e)}"}), 500


# GET ALL APPOINTMENTS
@views.route('/api/appointments/all', methods=['GET'])
@roles_required('admin')
def get_all_appointments():
    """Get all appointments with filtering options"""
    
    # Query parameters for filtering
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    doctor_id = request.args.get('doctor_id')
    patient_id = request.args.get('patient_id')
    
    try:
        from datetime import datetime as dt
        
        # Start with base query
        query = Appointment.query
        
        # Apply filters
        if status:
            query = query.filter_by(status=status)
        
        if doctor_id:
            query = query.filter_by(doctor_id=int(doctor_id))
        
        if patient_id:
            query = query.filter_by(patient_id=int(patient_id))
        
        if date_from:
            date_from_obj = dt.fromisoformat(date_from).date()
            query = query.filter(Appointment.date >= date_from_obj)
        
        if date_to:
            date_to_obj = dt.fromisoformat(date_to).date()
            query = query.filter(Appointment.date <= date_to_obj)
        
        # Order by date and time (most recent first)
        appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
        
        appointments_list = []
        
        for appointment in appointments:
            # Get patient details
            patient = Patient.query.get(appointment.patient_id)
            patient_user = User.query.get(patient.user_id) if patient else None
            
            # Get doctor details
            doctor = Doctor.query.get(appointment.doctor_id)
            doctor_user = User.query.get(doctor.user_id) if doctor else None
            
            appointment_info = {
                "id": appointment.id,
                "date": appointment.date.isoformat() if appointment.date else None,
                "time": appointment.time.isoformat() if appointment.time else None,
                "status": appointment.status,
                "patient": {
                    "id": patient.id if patient else None,
                    "name": patient.name if patient else "N/A",
                    "age": patient.age if patient else None,
                    "contact": patient.contact if patient else None,
                    "username": patient_user.username if patient_user else None
                },
                "doctor": {
                    "id": doctor.id if doctor else None,
                    "name": doctor.name if doctor else "N/A",
                    "specialization": doctor.specialization if doctor else None,
                    "department_id": doctor.department_id if doctor else None
                },
                "has_treatment": appointment.treatment is not None
            }
            
            # Add treatment summary if exists
            if appointment.treatment:
                appointment_info["treatment_summary"] = {
                    "id": appointment.treatment.id,
                    "diagnosis": appointment.treatment.diagnosis,
                    "has_prescription": bool(appointment.treatment.prescription),
                    "medicine_count": len(appointment.treatment.medicine)
                }
            
            appointments_list.append(appointment_info)
        
        # Calculate statistics
        stats = {
            "total": len(appointments_list),
            "pending": len([a for a in appointments_list if a['status'] == 'Pending']),
            "completed": len([a for a in appointments_list if a['status'] == 'Completed']),
            "cancelled": len([a for a in appointments_list if a['status'] == 'Cancelled']),
            "with_treatment": len([a for a in appointments_list if a['has_treatment']])
        }
        
        return jsonify({
            "message": "Appointments retrieved successfully",
            "statistics": stats,
            "filters_applied": {
                "status": status,
                "date_from": date_from,
                "date_to": date_to,
                "doctor_id": doctor_id,
                "patient_id": patient_id
            },
            "appointments": appointments_list
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error retrieving appointments: {str(e)}"}), 500


# GET APPOINTMENT DETAILS
@views.route('/api/appointment/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment_details(appointment_id):
    """Get detailed information about a specific appointment"""
    
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    
    # Check authorization
    patient = Patient.query.get(appointment.patient_id)
    doctor = Doctor.query.get(appointment.doctor_id)
    
    # Only allow access to involved parties or admin
    authorized = False
    if current_user.role == 'admin':
        authorized = True
    elif current_user.role == 'patient' and patient and patient.user_id == current_user.id:
        authorized = True
    elif current_user.role == 'doctor' and doctor and doctor.user_id == current_user.id:
        authorized = True
    
    if not authorized:
        return jsonify({"message": "Access denied - You can only view your own appointments"}), 403
    
    try:
        # Get patient details
        patient_user = User.query.get(patient.user_id) if patient else None
        
        # Get doctor details
        doctor_user = User.query.get(doctor.user_id) if doctor else None
        
        appointment_info = {
            "id": appointment.id,
            "date": appointment.date.isoformat() if appointment.date else None,
            "time": appointment.time.isoformat() if appointment.time else None,
            "status": appointment.status,
            "patient": {
                "id": patient.id if patient else None,
                "name": patient.name if patient else "N/A",
                "age": patient.age if patient else None,
                "contact": patient.contact if patient else None,
                "user": {
                    "username": patient_user.username if patient_user else None,
                    "email": patient_user.email if patient_user else None
                }
            },
            "doctor": {
                "id": doctor.id if doctor else None,
                "name": doctor.name if doctor else "N/A",
                "specialization": doctor.specialization if doctor else None,
                "experience": doctor.experience if doctor else None,
                "user": {
                    "username": doctor_user.username if doctor_user else None,
                    "email": doctor_user.email if doctor_user else None
                }
            }
        }
        
        # Add treatment details if exists
        if appointment.treatment:
            treatment = appointment.treatment
            medicines = []
            
            for medicine in treatment.medicine:
                medicines.append({
                    "id": medicine.id,
                    "name": medicine.name,
                    "description": medicine.description
                })
            
            appointment_info["treatment"] = {
                "id": treatment.id,
                "diagnosis": treatment.diagnosis,
                "prescription": treatment.prescription,
                "notes": treatment.notes,
                "medicines": medicines
            }
        
        return jsonify({
            "message": "Appointment details retrieved successfully",
            "appointment": appointment_info
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error retrieving appointment details: {str(e)}"}), 500


# GET APPOINTMENTS HISTORY
@views.route('/api/appointments/history', methods=['GET'])
@jwt_required()
def get_appointments_history():
    """Get user's appointment history with treatment details"""
    try:
        user_id = current_user.id
        
        if current_user.role == 'patient':
            appointments = Appointment.query.join(Patient).filter(
                Patient.user_id == user_id
            ).all()
            # Get patient info
            patient = Patient.query.filter_by(user_id=user_id).first()
            patient_info = {
                'name': f"{current_user.first_name} {current_user.last_name}",
                'doctor_name': None,
                'department': None
            }
        elif current_user.role == 'doctor':
            appointments = Appointment.query.filter_by(doctor_id=current_user.doctor.id).all()
            patient_info = None
        else:
            appointments = Appointment.query.all()
            patient_info = None
        
        visits = []
        for apt in appointments:
            visit = {
                'visit_no': apt.id,
                'visit_type': 'In-person',
                'date': apt.date.isoformat() if apt.date else None,
                'time': apt.time.isoformat() if apt.time else None,
                'status': apt.status,
                'tests_done': '',
                'diagnosis': '',
                'prescription': '',
                'medicines': ''
            }
            
            # Get treatment details if they exist
            if apt.treatment:
                visit['diagnosis'] = apt.treatment.diagnosis or ''
                visit['prescription'] = apt.treatment.prescription or ''
                visit['notes'] = apt.treatment.notes or ''
                
                # Get medicines
                if apt.treatment.medicine:
                    medicine_names = [med.name for med in apt.treatment.medicine]
                    visit['medicines'] = ', '.join(medicine_names) if medicine_names else ''
            
            visits.append(visit)
        
        # Set first doctor info for patient view
        if current_user.role == 'patient' and visits and patient_info:
            first_appointment = appointments[0] if appointments else None
            if first_appointment and first_appointment.doctor:
                patient_info['doctor_name'] = first_appointment.doctor.name
                patient_info['department'] = first_appointment.doctor.specialization
        
        return jsonify({
            'patient_info': patient_info,
            'visits': visits,
            'statistics': {
                'total_appointments': len(visits),
                'pending_appointments': len([v for v in visits if v['status'] == 'Pending']),
                'completed_appointments': len([v for v in visits if v['status'] == 'Completed']),
                'cancelled_appointments': len([v for v in visits if v['status'] == 'Cancelled'])
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f"Error: {str(e)}"}), 500