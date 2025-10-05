# from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from app.database import db
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
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Float)
    department = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

# Patient Class
class Patient(db.Model):
    __tablename__ = 'patient'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Appointment Class
class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(100), nullable=False)

# Treatment Class
class Treatment(db.Model):
    __tablename__ = 'treatment'

    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.String(100), nullable=False)
    prescription = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(100), nullable=False)

# Department Class
class Department(db.Model):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)

# Medicine Class
class Medicine(db.Model):
    __tablename__ = 'medicine'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)