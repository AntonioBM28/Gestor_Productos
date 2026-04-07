from flask import Blueprint, request, jsonify, current_app
from models import serialize_user, to_object_id
from middleware import admin_required

users_bp = Blueprint('users', __name__)


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
        return jsonify({'error': 'Invalid user ID'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    new_role = data.get('role', '').strip()
    valid_roles = ['user', 'admin']

    if new_role not in valid_roles:
        return jsonify({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400

    users_col = current_app.config['USERS_COLLECTION']

    user = users_col.find_one({'_id': oid})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    users_col.update_one(
        {'_id': oid},
        {'$set': {'role': new_role}}
    )

    updated_user = users_col.find_one({'_id': oid})

    return jsonify({
        'message': f'User role updated to {new_role}',
        'user': serialize_user(updated_user)
    }), 200


@users_bp.route('/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)."""
    oid = to_object_id(user_id)
    if not oid:
        return jsonify({'error': 'Invalid user ID'}), 400

    users_col = current_app.config['USERS_COLLECTION']
    cart_col = current_app.config['CART_ITEMS_COLLECTION']
    orders_col = current_app.config['ORDERS_COLLECTION']

    user = users_col.find_one({'_id': oid})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Prevent deleting yourself
    from flask_jwt_extended import get_jwt_identity
    current_user_id = get_jwt_identity()
    if str(oid) == current_user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400

    # Clean up user's data
    cart_col.delete_many({'user_id': oid})

    # Delete the user
    users_col.delete_one({'_id': oid})

    return jsonify({'message': 'User deleted successfully'}), 200
