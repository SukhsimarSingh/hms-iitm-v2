# from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from backend.database import db
from sqlalchemy.sql import func

# DB MODELS
# User Class
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    confirmed_at = db.Column(db.DateTime(), default=func.now())

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, default='')

    role = db.Column(db.String(255), nullable=False, default='patient')

    doctor = db.relationship('Doctor', backref='user', uselist=False)

    def __repr__(self) -> str:
        return f'User with the {self.id} and {self.email} created successfully'

    def set_password(self, password):
        hashed_pwd = bcrypt.hashpw(password=password.encode('utf-8'), salt=bcrypt.gensalt())
        self.password = hashed_pwd
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

# Doctor Class
class Doctor(db.Model):
    __tablename__ = 'doctor'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)
    specialization = db.Column(db.String, nullable=False)
    experience = db.Column(db.Float)

    availability = db.Column(db.String, nullable=False, default='Available')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)

    appointment = db.relationship('Appointment', backref='doctor')
    department = db.relationship('Department', backref='doctors')

# Patient Class
class Patient(db.Model):
    __tablename__ = 'patient'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment = db.relationship('Appointment', backref='patient')

# Appointment Class
class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)

    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    status = db.Column(db.String, nullable=False)
    treatment = db.relationship('Treatment', backref='appointment', uselist=False)

# Treatment Class
class Treatment(db.Model):
    __tablename__ = 'treatment'

    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)

    diagnosis = db.Column(db.String, nullable=False)
    prescription = db.Column(db.String, nullable=False)
    notes = db.Column(db.String, nullable=False)

    medicine = db.relationship('Medicine', backref='treatment')

# Department Class
class Department(db.Model):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        return f'Department: {self.name}'

# Medicine Class
class Medicine(db.Model):
    __tablename__ = 'medicine'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    treatment_id = db.Column(db.Integer, db.ForeignKey('treatment.id'), nullable=False)