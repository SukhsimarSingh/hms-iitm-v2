from flask import Flask

from .database import db
from .models import User
from .config import Config
from .security import jwt
from datetime import datetime

# Creating and Configuring app
def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(email='admin@me.com').one_or_none()

        if not admin:
            db.session.add(User(email='admin@me.com', password='password', 
                        confirmed_at=datetime.now(), first_name='fname', last_name='lname'))
            db.session.commit()
    
    return app

app = create_app()