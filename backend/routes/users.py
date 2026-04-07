"""User management routes for Gestor de Productos.

Admin-only operations for listing users, changing roles, and deleting users.
All operations are logged and protected against self-modification attacks.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from models import serialize_user, to_object_id, RoleUpdateSchema
from middleware import admin_required
from security import log_security_event

users_bp = Blueprint('users', __name__)

# Schema instances
_role_schema = RoleUpdateSchema()


@users_bp.route('', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)."""
    users_col = current_app.config['USERS_COLLECTION']

    users = list(users_col.find().sort('created_at', -1))

    return jsonify({
        'users': [serialize_user(u) for u in users]
    }), 200


@users_bp.route('/<user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """Change a user's role (admin only)."""
    oid = to_object_id(user_id)
    if not oid:
        return jsonify({'error': 'ID de usuario inválido'}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # Validate with schema
    try:
        validated = _role_schema.load(data)
    except ValidationError as e:
        first_error = next(
            (msgs[0] for msgs in e.messages.values() if isinstance(msgs, list) and msgs),
            'Datos inválidos'
        )
        return jsonify({'error': first_error}), 400

    new_role = validated['role']
    current_admin_id = get_jwt_identity()

    # Prevent admin from changing their own role
    if str(oid) == current_admin_id:
        return jsonify({'error': 'No puedes cambiar tu propio rol'}), 400

    users_col = current_app.config['USERS_COLLECTION']

    user = users_col.find_one({'_id': oid})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    old_role = user.get('role', 'user')

    # Prevent removing the last admin
    if old_role == 'admin' and new_role != 'admin':
        admin_count = users_col.count_documents({'role': 'admin'})
        if admin_count <= 1:
            return jsonify({
                'error': 'No se puede quitar el rol de administrador. Debe haber al menos un admin'
            }), 400

    users_col.update_one(
        {'_id': oid},
        {'$set': {'role': new_role}}
    )

    updated_user = users_col.find_one({'_id': oid})

    log_security_event(
        'ROLE_CHANGED',
        f'target_user={user_id} old_role={old_role} new_role={new_role}',
        current_admin_id
    )

    return jsonify({
        'message': f'Rol de usuario actualizado a {new_role}',
        'user': serialize_user(updated_user)
    }), 200


@users_bp.route('/<user_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_user_active(user_id):
    """Activate or deactivate a user account (admin only)."""
    oid = to_object_id(user_id)
    if not oid:
        return jsonify({'error': 'ID de usuario inválido'}), 400

    current_admin_id = get_jwt_identity()

    # Prevent admin from deactivating themselves
    if str(oid) == current_admin_id:
        return jsonify({'error': 'No puedes desactivar tu propia cuenta'}), 400

    users_col = current_app.config['USERS_COLLECTION']

    user = users_col.find_one({'_id': oid})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    new_status = not user.get('is_active', True)

    users_col.update_one(
        {'_id': oid},
        {'$set': {'is_active': new_status}}
    )

    updated_user = users_col.find_one({'_id': oid})

    status_text = 'activada' if new_status else 'desactivada'
    log_security_event(
        'ACCOUNT_STATUS_CHANGED',
        f'target_user={user_id} is_active={new_status}',
        current_admin_id
    )

    return jsonify({
        'message': f'Cuenta {status_text} exitosamente',
        'user': serialize_user(updated_user)
    }), 200


@users_bp.route('/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)."""
    oid = to_object_id(user_id)
    if not oid:
        return jsonify({'error': 'ID de usuario inválido'}), 400

    current_admin_id = get_jwt_identity()

    # Prevent deleting yourself
    if str(oid) == current_admin_id:
        return jsonify({'error': 'No puedes eliminar tu propia cuenta'}), 400

    users_col = current_app.config['USERS_COLLECTION']
    cart_col = current_app.config['CART_ITEMS_COLLECTION']

    user = users_col.find_one({'_id': oid})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Prevent deleting the last admin
    if user.get('role') == 'admin':
        admin_count = users_col.count_documents({'role': 'admin'})
        if admin_count <= 1:
            return jsonify({
                'error': 'No se puede eliminar el último administrador'
            }), 400

    # Clean up user's data
    cart_col.delete_many({'user_id': oid})

    # Revoke all user's tokens by blacklisting
    blacklist = current_app.config.get('TOKEN_BLACKLIST_COLLECTION')
    if blacklist:
        from datetime import datetime, timezone
        blacklist.insert_one({
            'jti': f'user_deleted_{user_id}',
            'token_type': 'all',
            'user_id': str(oid),
            'created_at': datetime.now(timezone.utc)
        })

    # Delete the user
    users_col.delete_one({'_id': oid})

    log_security_event(
        'USER_DELETED',
        f'target_user={user_id} username={user.get("username")}',
        current_admin_id
    )

    return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
