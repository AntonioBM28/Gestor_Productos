from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import serialize_cart_item, to_object_id
from datetime import datetime, timezone

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    """Get the current user's cart items."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    if not user_oid:
        return jsonify({'error': 'Invalid user ID'}), 400

    cart_col = current_app.config['CART_ITEMS_COLLECTION']
    products_col = current_app.config['PRODUCTS_COLLECTION']

    cart_items = list(cart_col.find({'user_id': user_oid}))

    items_with_products = []
    total = 0.0

    for item in cart_items:
        product = products_col.find_one({'_id': item['product_id']})
        if product:
            total += product['price'] * item['quantity']
        items_with_products.append(serialize_cart_item(item, product))

    return jsonify({
        'items': items_with_products,
        'total': round(total, 2),
        'count': len(items_with_products)
    }), 200


@cart_bp.route('', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add a product to the cart."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    if not user_oid:
        return jsonify({'error': 'Invalid user ID'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    product_oid = to_object_id(product_id)
    if not product_oid:
        return jsonify({'error': 'Invalid product ID'}), 400

    products_col = current_app.config['PRODUCTS_COLLECTION']
    cart_col = current_app.config['CART_ITEMS_COLLECTION']

    product = products_col.find_one({'_id': product_oid})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if product['stock'] < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400

    # Check if product already in cart
    existing = cart_col.find_one({'user_id': user_oid, 'product_id': product_oid})

    if existing:
        new_qty = existing['quantity'] + quantity
        if product['stock'] < new_qty:
            return jsonify({'error': 'Not enough stock available'}), 400
        cart_col.update_one(
            {'_id': existing['_id']},
            {'$set': {'quantity': new_qty}}
        )
    else:
        cart_col.insert_one({
            'user_id': user_oid,
            'product_id': product_oid,
            'quantity': quantity,
            'added_at': datetime.now(timezone.utc)
        })

    return jsonify({'message': 'Product added to cart'}), 201


@cart_bp.route('/<item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    item_oid = to_object_id(item_id)

    if not user_oid or not item_oid:
        return jsonify({'error': 'Invalid ID'}), 400

    data = request.get_json()
    cart_col = current_app.config['CART_ITEMS_COLLECTION']
    products_col = current_app.config['PRODUCTS_COLLECTION']

    cart_item = cart_col.find_one({'_id': item_oid, 'user_id': user_oid})
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404

    quantity = data.get('quantity', 1)

    if quantity <= 0:
        cart_col.delete_one({'_id': item_oid})
    else:
        product = products_col.find_one({'_id': cart_item['product_id']})
        if product and product['stock'] < quantity:
            return jsonify({'error': 'Not enough stock'}), 400
        cart_col.update_one(
            {'_id': item_oid},
            {'$set': {'quantity': quantity}}
        )

    return jsonify({'message': 'Cart updated'}), 200


@cart_bp.route('/<item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove an item from the cart."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    item_oid = to_object_id(item_id)

    if not user_oid or not item_oid:
        return jsonify({'error': 'Invalid ID'}), 400

    cart_col = current_app.config['CART_ITEMS_COLLECTION']

    result = cart_col.delete_one({'_id': item_oid, 'user_id': user_oid})
    if result.deleted_count == 0:
        return jsonify({'error': 'Cart item not found'}), 404

    return jsonify({'message': 'Item removed from cart'}), 200


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from the cart."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    if not user_oid:
        return jsonify({'error': 'Invalid user ID'}), 400

    cart_col = current_app.config['CART_ITEMS_COLLECTION']
    cart_col.delete_many({'user_id': user_oid})

    return jsonify({'message': 'Cart cleared'}), 200
