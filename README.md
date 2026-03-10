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

- **User**: Core user model with authentication
- **Doctor**: Doctor-specific information and relationships
- **Patient**: Patient information
- **Appointment**: Appointment scheduling
- **Treatment**: Treatment records and prescriptions
- **Medicine**: Medicine inventory and prescriptions

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

### Dashboard
- `GET /api/dashboard` - User dashboard (requires JWT)
- `GET /admin` - Admin dashboard (admin only)

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

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
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

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Role-based authorization decorators
- Protected API endpoints
- SQL injection prevention through ORM

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

Sukh Singh
