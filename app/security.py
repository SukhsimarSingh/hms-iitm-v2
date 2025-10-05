from flask_jwt_extended import JWTManager, current_user, jwt_required
from flask import jsonify
from functools import wraps

from .models import User

jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

def roles_required(required_role):
    def wrapper(func):
        @wraps(func)
        @jwt_required()
        def decorator(*args, **kwargs):
            if current_user.role!=required_role:
                return jsonify(message = "Access Denined - Insufficient role"), 403
            return func(*args, **kwargs)
        return decorator
    return wrapper