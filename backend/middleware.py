from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import to_object_id


def admin_required(fn):
    """Decorator that requires the user to be an admin."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        oid = to_object_id(user_id)
        if not oid:
            return jsonify({'error': 'Invalid user ID'}), 400

        users = current_app.config['USERS_COLLECTION']
        user = users.find_one({'_id': oid})

        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def user_required(fn):
    """Decorator that requires the user to be authenticated (any role)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        oid = to_object_id(user_id)
        if not oid:
            return jsonify({'error': 'Invalid user ID'}), 400

        users = current_app.config['USERS_COLLECTION']
        user = users.find_one({'_id': oid})

        if not user:
            return jsonify({'error': 'User not found'}), 404
        return fn(*args, **kwargs)
    return wrapper
