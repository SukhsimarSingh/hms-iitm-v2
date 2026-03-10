# Hospital Management System V2

A comprehensive Hospital Management System built for IITM MAD2 course using Python, Flask, and SQLAlchemy with JWT authentication.

## Features

- **User Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (Admin, Doctor, Patient)
  - Secure password hashing using bcrypt
  - User registration and login

- **User Management**
  - Admin dashboard for managing users
  - Doctor and patient profile management
  - User role assignment
  - Blacklist/ban functionality for deactivating accounts

- **Doctor Management**
  - Add and manage doctors
  - Track specialization, experience, and department
  - Doctor availability tracking
  - Link doctors to user accounts

- **Appointment System**
  - Schedule appointments between patients and doctors
  - Track appointment status
  - Date and time management

- **Treatment Records**
  - Diagnosis tracking
  - Prescription management
  - Treatment notes
  - Medicine tracking

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Authentication**: Flask-JWT-Extended
- **Password Hashing**: bcrypt
- **Database Migrations**: Flask-Migrate
- **Environment Management**: python-dotenv

## Project Structure

```
hms-iitm-v2/
├── app/
│   ├── __init__.py          # App factory and initialization
│   ├── auth.py              # Authentication routes
│   ├── routes.py            # Main application routes
│   ├── models.py            # Database models
│   ├── database.py          # Database configuration
│   ├── security.py          # JWT and role-based security
│   └── config.py            # Application configuration
├── main.py                  # Application entry point
└── README.md
```

## Database Models

- **User**: Core user model with authentication (username, email, password, role, active status)
- **Doctor**: Doctor-specific information (name, specialization, experience, availability, department)
- **Patient**: Patient information (name, age, contact, search_keyword)
- **Appointment**: Appointment scheduling (patient_id, doctor_id, date, time, status)
- **Treatment**: Treatment records (appointment_id, diagnosis, prescription, notes)
- **Medicine**: Medicine inventory (name, description, treatment_id)
- **Department**: Hospital departments (name, description)

## API Endpoints

### Authentication
- `POST /auth/api/auth/register` - Register new user
- `POST /auth/api/auth/login` - Login and get JWT token
- `GET /auth/api/auth/profile` - Get current user profile (requires JWT)

### User Management
- `GET /api/get/<role>` - Get all users by role (patient/doctor)
- `GET /api/get/<role>/<username>` - Get specific user details

### Doctor Management
- `POST /api/add/doctor` - Add new doctor (admin only)
- `PUT/PATCH /api/update/doctor/<doctor_id>` - Update doctor details (admin only)
- `PUT/PATCH /api/doctor/availability` - Update doctor availability status (doctor only)
- `DELETE/POST /api/remove/doctor` - Remove doctor and associated user (admin only)
- `POST/PATCH /api/blacklist/doctor/<doctor_id>` - Blacklist/unblacklist doctor (admin only)

### Patient Management
- `PUT/PATCH /api/update/patient/<patient_id>` - Update patient user account (self or admin)
- `PUT/PATCH /api/patient/record/update/<patient_id>` - Update patient record: name, age, contact (self, doctor, or admin)
- `DELETE/POST /api/remove/patient` - Remove patient (admin only)
- `POST/PATCH /api/blacklist/patient/<patient_id>` - Blacklist/unblacklist patient (admin only)

### Blacklist Management
- `GET /api/blacklist/list` - Get all blacklisted users (admin only)

### Dashboard
- `GET /api/dashboard` - General dashboard (redirects to role-specific dashboard)
- `GET /api/admin/dashboard` - Comprehensive admin dashboard with all data (admin only)
- `GET /api/doctor/dashboard` - Doctor dashboard with appointments and patient history (doctor only)
- `GET /api/patient/dashboard` - Patient dashboard with appointments and available doctors (patient only)

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hms-iitm-v2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-migrate flask-jwt-extended bcrypt python-dotenv
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SQLALCHEMY_DATABASE_URI=sqlite:///hospital.db
   JWT_SECRET_KEY=your-secret-key-here
   SECRET_KEY=your-flask-secret-key
   SECURITY_PASSWORD_SALT=your-password-salt
   
   ADMIN_USERNAME=admin
   ADMIN_EMAIL=admin@hospital.com
   ADMIN_PASSWORD=admin123
   ```

5. **Initialize the database with Flask-Migrate**
   ```bash
   # Initialize migration repository (first time only)
   flask db init
   
   # Create initial migration
   flask db migrate -m "Initial migration"
   
   # Apply migration to create tables
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

   The application will be available at `http://localhost:5000`

## Default Admin Account

On first run, an admin account is automatically created with credentials from your `.env` file:
- Username: As specified in `ADMIN_USERNAME`
- Email: As specified in `ADMIN_EMAIL`
- Password: As specified in `ADMIN_PASSWORD`

## Development Notes

- The application uses SQLAlchemy 2.0 style with `Mapped` type annotations for better type checking
- All passwords are hashed using bcrypt before storage
- JWT tokens are required for protected routes
- Role-based access control ensures proper authorization

## Admin Dashboard

The admin dashboard provides a comprehensive view of all system data in a single API call, perfect for displaying on an admin interface.

### Endpoint: `GET /api/admin/dashboard`

**Authorization**: Admin only

**Response Structure**:
```json
{
  "message": "Admin dashboard data retrieved successfully",
  "admin": {
    "username": "admin",
    "email": "admin@hospital.com",
    "first_name": "Admin",
    "last_name": "User"
  },
  "statistics": {
    "total_doctors": 10,
    "active_doctors": 8,
    "blacklisted_doctors": 2,
    "total_patients": 50,
    "active_patients": 48,
    "blacklisted_patients": 2,
    "total_appointments": 25,
    "pending_appointments": 5,
    "completed_appointments": 20
  },
  "registered_doctors": [
    {
      "user_id": 2,
      "username": "dr.abcde",
      "email": "abcde@hospital.com",
      "first_name": "Dr.",
      "last_name": "Abcde",
      "active": true,
      "doctor_id": 1,
      "name": "Dr. Abcde",
      "specialization": "Cardiology",
      "department": "Heart Center",
      "experience": 10.5,
      "availability": "Available"
    }
  ],
  "registered_patients": [
    {
      "user_id": 3,
      "username": "mr.abcde",
      "email": "patient@email.com",
      "first_name": "Mr.",
      "last_name": "Abcde",
      "active": true
    }
  ],
  "upcoming_appointments": [
    {
      "id": 1,
      "date": "2026-03-15",
      "time": "10:00:00",
      "status": "pending",
      "patient": {
        "id": 3,
        "name": "Mr. Abcde",
        "username": "mr.abcde"
      },
      "doctor": {
        "id": 1,
        "name": "Dr. Parst",
        "specialization": "Cardiology",
        "department": "Heart Center"
      }
    }
  ]
}
```

### Features:
- **Single API Call**: All dashboard data in one request
- **Statistics Summary**: Quick overview of system metrics
- **Complete User Lists**: All doctors and patients with full details
- **Appointment Overview**: All appointments with patient and doctor info
- **Active Status**: Shows which users are active or blacklisted
- **Ready for UI**: Structured data perfect for frontend rendering

## Doctor Dashboard

The doctor dashboard provides doctors with their appointments, patient history, and schedule management.

### Endpoint: `GET /api/doctor/dashboard`

**Authorization**: Doctor only

**Response Structure**:
```json
{
  "message": "Doctor dashboard data retrieved successfully",
  "doctor": {
    "user_id": 2,
    "doctor_id": 1,
    "username": "dr.abcde",
    "email": "abcde@hospital.com",
    "name": "Dr. Abcde",
    "first_name": "Dr.",
    "last_name": "Abcde",
    "specialization": "Cardiology",
    "department": "Heart Center",
    "experience": 10.5,
    "availability": "Available"
  },
  "statistics": {
    "total_appointments": 25,
    "upcoming_appointments": 5,
    "completed_appointments": 20,
    "total_patients": 15
  },
  "upcoming_appointments": [
    {
      "id": 1,
      "date": "2026-03-15",
      "time": "10:00:00",
      "status": "pending",
      "patient": {
        "id": 1,
        "name": "Mr. Abcde",
        "age": 45,
        "contact": "1234567890",
        "username": "mr.abcde",
        "email": "patient@email.com"
      },
      "treatment": {
        "id": 1,
        "diagnosis": "Hypertension",
        "prescription": "Medicine XYZ",
        "notes": "Follow-up in 2 weeks"
      }
    }
  ],
  "patient_history": [
    {
      "patient_id": 1,
      "name": "Mr. Abcde",
      "age": 45,
      "contact": "1234567890",
      "username": "mr.abcde",
      "email": "patient@email.com",
      "total_appointments": 3,
      "last_visit": "2026-03-10"
    }
  ]
}
```

### Features:
- **Doctor Profile**: Complete doctor information
- **Statistics**: Quick metrics for appointments and patients
- **Upcoming Appointments**: All scheduled appointments with patient details
- **Patient History**: All patients seen with visit counts and last visit date
- **Treatment Records**: Access to diagnosis, prescriptions, and notes

## Patient Dashboard

The patient dashboard provides patients with their appointments, medical history, and available doctors.

### Endpoint: `GET /api/patient/dashboard`

**Authorization**: Patient only

**Response Structure**:
```json
{
  "message": "Patient dashboard data retrieved successfully",
  "patient": {
    "user_id": 3,
    "patient_id": 1,
    "username": "mr.abcde",
    "email": "patient@email.com",
    "first_name": "Mr.",
    "last_name": "Abcde",
    "name": "Mr. Abcde",
    "age": 45,
    "contact": "1234567890"
  },
  "statistics": {
    "total_appointments": 10,
    "upcoming_appointments": 2,
    "completed_appointments": 7,
    "cancelled_appointments": 1
  },
  "upcoming_appointments": [
    {
      "id": 1,
      "date": "2026-03-15",
      "time": "10:00:00",
      "status": "pending",
      "doctor": {
        "id": 1,
        "name": "Dr. Parst",
        "specialization": "Cardiology",
        "department": "Heart Center",
        "experience": 10.5,
        "username": "dr.parst",
        "email": "parst@hospital.com"
      },
      "treatment": {
        "id": 1,
        "diagnosis": "Hypertension",
        "prescription": "Medicine XYZ",
        "notes": "Follow-up in 2 weeks",
        "medicines": [
          {
            "id": 1,
            "name": "Medicine XYZ",
            "description": "Take twice daily"
          }
        ]
      }
    }
  ],
  "departments": ["Cardiology", "Neurology", "Orthopedics"],
  "doctors_by_department": {
    "Cardiology": [
      {
        "doctor_id": 1,
        "name": "Dr. Parst",
        "specialization": "Cardiology",
        "experience": 10.5,
        "availability": "Available"
      }
    ]
  }
}
```

### Features:
- **Patient Profile**: Complete patient information
- **Statistics**: Appointment counts by status
- **Upcoming Appointments**: All scheduled appointments with doctor and treatment details
- **Medical History**: Past treatments, diagnoses, and prescriptions
- **Medicine List**: Detailed medicine information for each treatment
- **Available Doctors**: List of doctors by department for booking appointments
- **Department List**: All available departments in the hospital

## Blacklist/Ban Feature

The system includes a comprehensive blacklist feature that allows administrators to deactivate user accounts without permanently deleting them:

### How It Works

- **Soft Deactivation**: When a user is blacklisted, their `active` status is set to `False`
- **Login Prevention**: Blacklisted users cannot log in and receive a clear error message
- **Data Preservation**: All user data, appointments, and history are preserved
- **Reversible**: Admins can reactivate accounts by toggling the blacklist status
- **Flexible API**: Can toggle status or explicitly set active/inactive state

### Usage Examples

**Blacklist a doctor:**
```bash
POST /api/blacklist/doctor/123
# Toggles the active status

# Or explicitly set status:
POST /api/blacklist/doctor/123
{
  "active": false
}
```

**Reactivate a user:**
```bash
POST /api/blacklist/doctor/123
{
  "active": true
}
```

**View all blacklisted users:**
```bash
GET /api/blacklist/list
```

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Role-based authorization decorators
- Protected API endpoints
- SQL injection prevention through ORM
- Account deactivation/blacklist system

## Future Enhancements

- Email notifications for appointments
- Patient medical history tracking
- Billing and payment integration
- Report generation
- Real-time appointment availability
- Multi-language support

## License

This project is built for educational purposes as part of IITM MAD2 course.

## Author

Sukhsimar Singh
