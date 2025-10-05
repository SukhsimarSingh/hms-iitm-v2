from flask import Flask

from .database import db
from .models import User
from .config import Config
from .security import jwt
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# Creating and Configuring app
def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(email=ADMIN_EMAIL).one_or_none()

        if not admin:
            _admin = User(username=ADMIN_USERNAME, email=ADMIN_EMAIL, confirmed_at=datetime.now(), 
                          first_name='Sukh', last_name='Singh', role='admin')
            
            _admin.set_password(ADMIN_PASSWORD)

            db.session.add(_admin)
            db.session.commit()
    
    return app

app = create_app()