from flask import Flask
from flask_migrate import Migrate
from datetime import datetime
from dotenv import load_dotenv
import os

from .database import db
from .models import User
from .config import Config
from .security import jwt

load_dotenv()

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# Creating and Configuring app
def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(Config)

    from .auth import auth
    from .routes import views

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    
    db.init_app(app)
    jwt.init_app(app)
    
    migrate = Migrate(app=app, db=db, render_as_batch=True)

    with app.app_context():

        admin = User.query.filter_by(email=ADMIN_EMAIL).one_or_none()

        if not admin:
            _admin = User(username=ADMIN_USERNAME, email=ADMIN_EMAIL, confirmed_at=datetime.now(), # type: ignore
                          first_name='Sukh', last_name='Singh', role='admin')  # type: ignore
            
            _admin.set_password(ADMIN_PASSWORD)

            try:
                db.session.add(_admin)
                db.session.commit()
                app.logger.info('Admin added successfully')

            except Exception as e:
                db.session.rollback()
                app.logger.info('%s Error adding admin', e)

    return app