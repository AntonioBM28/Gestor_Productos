"""Authentication routes for Gestor de Productos.

Includes registration, login, logout, token refresh, password change,
and current user retrieval. All endpoints are rate-limited and inputs
are validated and sanitized.
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from marshmallow import ValidationError
from models import (
    serialize_user, to_object_id,
    UserRegistrationSchema, UserLoginSchema, ChangePasswordSchema
)
from security import (
    validate_password_strength, sanitize_string,
    log_security_event, check_account_lockout
)
from middleware import get_current_user, user_required
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

# Schema instances (reusable)
_register_schema = UserRegistrationSchema()
_login_schema = UserLoginSchema()
_change_password_schema = ChangePasswordSchema()


# ─── Register ─────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    from app import limiter
    limiter.limit('3/minute')(lambda: None)()  # Manual rate limit check

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # Validate with Marshmallow schema
    try:
        validated = _register_schema.load(data)
    except ValidationError as e:
        errors = e.messages
        first_error = next(
            (msgs[0] for msgs in errors.values() if isinstance(msgs, list) and msgs),
            'Datos inválidos'
        )
        return jsonify({'error': first_error}), 400

    # Validate password strength
    is_strong, pwd_error = validate_password_strength(data.get('password', ''))
    if not is_strong:
        return jsonify({'error': pwd_error}), 400

    username = validated['username']
    email = validated['email']
    password = data['password']  # Use raw password for hashing

    users = current_app.config['USERS_COLLECTION']

    # Check uniqueness
    if users.find_one({'username': username}):
        return jsonify({'error': 'El nombre de usuario ya está en uso'}), 409

    if users.find_one({'email': email}):
        return jsonify({'error': 'El email ya está registrado'}), 409

    # Create user document
    user_doc = {
        'username': username,
        'email': email,
        'password_hash': generate_password_hash(password),
        'role': 'user',
        'is_active': True,
        'created_at': datetime.now(timezone.utc)
    }

    result = users.insert_one(user_doc)
    user_doc['_id'] = result.inserted_id

    user_id_str = str(user_doc['_id'])
    access_token = create_access_token(identity=user_id_str)
    refresh_token = create_refresh_token(identity=user_id_str)

    log_security_event('REGISTER', f'username={username} email={email}', user_id_str)

    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'user': serialize_user(user_doc),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


# ─── Login ────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return JWT tokens."""
    from app import limiter
    limiter.limit('5/minute')(lambda: None)()  # Manual rate limit check

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # Validate with schema
    try:
        validated = _login_schema.load(data)
    except ValidationError:
        return jsonify({'error': 'Email y contraseña son obligatorios'}), 400

    email = validated['email']
    password = validated['password']

    # Check account lockout
    is_locked, remaining_minutes = check_account_lockout(email)
    if is_locked:
        log_security_event('LOGIN_LOCKED', f'email={email}', level='warning')
        return jsonify({
            'error': f'Cuenta bloqueada temporalmente. Intenta de nuevo en {remaining_minutes} minutos'
        }), 429

    users = current_app.config['USERS_COLLECTION']
    user = users.find_one({'email': email})

    # Constant-time comparison to prevent user enumeration
    if not user:
        # Still hash a password to keep timing consistent
        generate_password_hash('dummy-password-for-timing')
        log_security_event('LOGIN_FAILED', f'email={email} reason=user_not_found', level='warning')
        return jsonify({'error': 'Email o contraseña inválidos'}), 401

    if not check_password_hash(user['password_hash'], password):
        log_security_event(
            'LOGIN_FAILED',
            f'email={email} reason=wrong_password',
            str(user['_id']),
            level='warning'
        )
        return jsonify({'error': 'Email o contraseña inválidos'}), 401

    # Check if account is active
    if not user.get('is_active', True):
        log_security_event(
            'LOGIN_INACTIVE',
            f'email={email}',
            str(user['_id']),
            level='warning'
        )
        return jsonify({'error': 'Cuenta desactivada. Contacta al administrador'}), 403

    user_id_str = str(user['_id'])
    access_token = create_access_token(identity=user_id_str)
    refresh_token = create_refresh_token(identity=user_id_str)

    log_security_event('LOGIN_SUCCESS', f'email={email}', user_id_str)

    return jsonify({
        'message': 'Inicio de sesión exitoso',
        'user': serialize_user(user),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


# ─── Refresh Token ────────────────────────────────────────────────────────────

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Get a new access token using a valid refresh token."""
    user_id = get_jwt_identity()

    # Verify user still exists and is active
    users = current_app.config['USERS_COLLECTION']
    oid = to_object_id(user_id)
    if not oid:
        return jsonify({'error': 'Token inválido'}), 401

    user = users.find_one({'_id': oid})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    if not user.get('is_active', True):
        return jsonify({'error': 'Cuenta desactivada'}), 403

    new_access_token = create_access_token(identity=user_id)

    return jsonify({
        'access_token': new_access_token
    }), 200


# ─── Logout ──────────────────────────────────────────────────────────────────

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(verify_type=False)
def logout():
    """Revoke the current JWT token by adding it to the blacklist."""
    jwt_data = get_jwt()
    jti = jwt_data['jti']
    token_type = jwt_data.get('type', 'access')
    user_id = get_jwt_identity()

    blacklist = current_app.config['TOKEN_BLACKLIST_COLLECTION']

    try:
        blacklist.insert_one({
            'jti': jti,
            'token_type': token_type,
            'user_id': user_id,
            'created_at': datetime.now(timezone.utc)
        })
    except Exception:
        pass  # Token might already be blacklisted

    log_security_event('LOGOUT', f'token_type={token_type}', user_id)

    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200


# ─── Change Password ─────────────────────────────────────────────────────────

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change the current user's password."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # Validate schema
    try:
        validated = _change_password_schema.load(data)
    except ValidationError as e:
        errors = e.messages
        first_error = next(
            (msgs[0] for msgs in errors.values() if isinstance(msgs, list) and msgs),
            'Datos inválidos'
        )
        return jsonify({'error': first_error}), 400

    # Validate new password strength
    is_strong, pwd_error = validate_password_strength(validated['new_password'])
    if not is_strong:
        return jsonify({'error': pwd_error}), 400

    user_id = get_jwt_identity()
    oid = to_object_id(user_id)
    if not oid:
        return jsonify({'error': 'ID de usuario inválido'}), 400

    users = current_app.config['USERS_COLLECTION']
    user = users.find_one({'_id': oid})

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Verify current password
    if not check_password_hash(user['password_hash'], validated['current_password']):
        log_security_event('PASSWORD_CHANGE_FAILED', 'wrong_current_password', user_id, level='warning')
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401

    # Prevent reusing the same password
    if check_password_hash(user['password_hash'], validated['new_password']):
        return jsonify({'error': 'La nueva contraseña no puede ser igual a la actual'}), 400

    # Update password
    users.update_one(
        {'_id': oid},
        {'$set': {'password_hash': generate_password_hash(validated['new_password'])}}
    )

    log_security_event('PASSWORD_CHANGED', '', user_id)

    return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200


# ─── Get Current User ────────────────────────────────────────────────────────

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_route():
    """Get the currently authenticated user's profile."""
    user_id = get_jwt_identity()
    users = current_app.config['USERS_COLLECTION']

    oid = to_object_id(user_id)
    if not oid:
        return jsonify({'error': 'ID de usuario inválido'}), 400

    user = users.find_one({'_id': oid})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    if not user.get('is_active', True):
        return jsonify({'error': 'Cuenta desactivada'}), 403

    return jsonify({'user': serialize_user(user)}), 200
