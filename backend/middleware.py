"""Authentication and authorization middleware for Gestor de Productos.

Provides role-based access control decorators and request context helpers.
"""
from functools import wraps
from flask import jsonify, current_app, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import to_object_id


def _load_current_user():
    """Load the current user into Flask's g context.

    Avoids querying the database multiple times per request.
    Returns the user document or None.
    """
    if hasattr(g, '_current_user'):
        return g._current_user

    try:
        verify_jwt_in_request()
    except Exception:
        g._current_user = None
        return None

    user_id = get_jwt_identity()
    oid = to_object_id(user_id)
    if not oid:
        g._current_user = None
        return None

    users = current_app.config['USERS_COLLECTION']
    user = users.find_one({'_id': oid})
    g._current_user = user
    return user


def get_current_user():
    """Get the current authenticated user from the request context.

    Must be called within a route protected by a role decorator.
    """
    return getattr(g, '_current_user', None)


def role_required(*roles):
    """Decorator that requires the user to have one of the specified roles.

    Usage:
        @role_required('admin')
        @role_required('user', 'admin')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = _load_current_user()

            if user is None:
                return jsonify({'error': 'Autenticación requerida'}), 401

            # Check if account is active
            if not user.get('is_active', True):
                return jsonify({'error': 'Cuenta desactivada. Contacta al administrador'}), 403

            user_role = user.get('role', 'user')
            if user_role not in roles:
                return jsonify({'error': 'No tienes permisos para esta acción'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Decorator that requires the user to be an admin."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = _load_current_user()

        if user is None:
            return jsonify({'error': 'Autenticación requerida'}), 401

        if not user.get('is_active', True):
            return jsonify({'error': 'Cuenta desactivada. Contacta al administrador'}), 403

        if user.get('role') != 'admin':
            return jsonify({'error': 'Se requieren permisos de administrador'}), 403

        return fn(*args, **kwargs)
    return wrapper


def user_required(fn):
    """Decorator that requires the user to be authenticated (any role)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = _load_current_user()

        if user is None:
            return jsonify({'error': 'Autenticación requerida'}), 401

        if not user.get('is_active', True):
            return jsonify({'error': 'Cuenta desactivada. Contacta al administrador'}), 403

        return fn(*args, **kwargs)
    return wrapper


def owner_or_admin(resource_user_id_field='user_id'):
    """Decorator that requires the user to own the resource or be admin.

    The resource_user_id_field is the field name in the resource document
    that contains the owner's user ID.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = _load_current_user()

            if user is None:
                return jsonify({'error': 'Autenticación requerida'}), 401

            if not user.get('is_active', True):
                return jsonify({'error': 'Cuenta desactivada. Contacta al administrador'}), 403

            # Admin can access any resource
            if user.get('role') == 'admin':
                return fn(*args, **kwargs)

            # For non-admins, the route handler must verify ownership
            return fn(*args, **kwargs)
        return wrapper
    return decorator
