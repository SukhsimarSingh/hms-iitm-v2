from dotenv import load_dotenv
import os

load_dotenv()

class Config():
    FLASK_ENV = os.environ.get("FLASK_ENV")
    DEBUG = os.environ.get("FLASK_DEBUG")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_VERIFY_SUB = False

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    
    # SECURITY_REGISTERABLE = True
    # SECURITY_SEND_REGISTER_EMAIL = False
    # SECURITY_RECOVERABLE = True
    # SECURITY_CHANGEABLE = True
    # SECURITY_UNAUTHORIZED_VIEW = None