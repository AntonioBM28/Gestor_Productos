from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import serialize_user, validate_user_data, to_object_id
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    is_valid, error = validate_user_data(data)
    if not is_valid:
        return jsonify({'error': error}), 400

    username = data['username'].strip()
    email = data['email'].strip()
    password = data['password']

    users = current_app.config['USERS_COLLECTION']

    # Check uniqueness
    if users.find_one({'username': username}):
        return jsonify({'error': 'Username already taken'}), 409

    if users.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 409

    # Create user document
    user_doc = {
        'username': username,
        'email': email,
        'password_hash': generate_password_hash(password),
        'role': 'user',
        'created_at': datetime.now(timezone.utc)
    }

    result = users.insert_one(user_doc)
    user_doc['_id'] = result.inserted_id

    access_token = create_access_token(identity=str(user_doc['_id']))

    return jsonify({
        'message': 'User registered successfully',
        'user': serialize_user(user_doc),
        'access_token': access_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    users = current_app.config['USERS_COLLECTION']
    user = users.find_one({'email': email})

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user['_id']))

    return jsonify({
        'message': 'Login successful',
        'user': serialize_user(user),
        'access_token': access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    users = current_app.config['USERS_COLLECTION']

    oid = to_object_id(user_id)
    if not oid:
        return jsonify({'error': 'Invalid user ID'}), 400

    user = users.find_one({'_id': oid})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': serialize_user(user)}), 200
