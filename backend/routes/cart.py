"""Cart routes for Gestor de Productos.

All cart operations require authentication. Inputs are validated
with Marshmallow schemas. Quantity and item limits are enforced.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from models import serialize_cart_item, to_object_id, CartItemSchema, CartUpdateSchema
from datetime import datetime, timezone

cart_bp = Blueprint('cart', __name__)

# Schema instances
_add_schema = CartItemSchema()
_update_schema = CartUpdateSchema()


@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    """Get the current user's cart items."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    if not user_oid:
        return jsonify({'error': 'ID de usuario inválido'}), 400

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
    from app import limiter
    limiter.limit('20/minute')(lambda: None)()

    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    if not user_oid:
        return jsonify({'error': 'ID de usuario inválido'}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # Validate with schema
    try:
        validated = _add_schema.load(data)
    except ValidationError as e:
        first_error = next(
            (msgs[0] for msgs in e.messages.values() if isinstance(msgs, list) and msgs),
            'Datos inválidos'
        )
        return jsonify({'error': first_error}), 400

    product_id = validated['product_id']
    quantity = validated['quantity']

    product_oid = to_object_id(product_id)
    if not product_oid:
        return jsonify({'error': 'ID de producto inválido'}), 400

    products_col = current_app.config['PRODUCTS_COLLECTION']
    cart_col = current_app.config['CART_ITEMS_COLLECTION']

    product = products_col.find_one({'_id': product_oid})
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404

    if product['stock'] < quantity:
        return jsonify({'error': 'No hay suficiente stock disponible'}), 400

    # Check cart item limit
    max_cart_items = current_app.config.get('MAX_CART_ITEMS', 50)
    current_cart_count = cart_col.count_documents({'user_id': user_oid})

    # Check if product already in cart
    existing = cart_col.find_one({'user_id': user_oid, 'product_id': product_oid})

    if existing:
        new_qty = existing['quantity'] + quantity
        max_qty = current_app.config.get('MAX_CART_QUANTITY', 100)
        if new_qty > max_qty:
            return jsonify({
                'error': f'La cantidad máxima por producto es {max_qty}'
            }), 400
        if product['stock'] < new_qty:
            return jsonify({'error': 'No hay suficiente stock disponible'}), 400
        cart_col.update_one(
            {'_id': existing['_id']},
            {'$set': {'quantity': new_qty}}
        )
    else:
        # Enforce cart item limit for new items
        if current_cart_count >= max_cart_items:
            return jsonify({
                'error': f'El carrito no puede tener más de {max_cart_items} productos diferentes'
            }), 400

        cart_col.insert_one({
            'user_id': user_oid,
            'product_id': product_oid,
            'quantity': quantity,
            'added_at': datetime.now(timezone.utc)
        })

    return jsonify({'message': 'Producto agregado al carrito'}), 201


@cart_bp.route('/<item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    item_oid = to_object_id(item_id)

    if not user_oid or not item_oid:
        return jsonify({'error': 'ID inválido'}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # Validate with schema
    try:
        validated = _update_schema.load(data)
    except ValidationError as e:
        first_error = next(
            (msgs[0] for msgs in e.messages.values() if isinstance(msgs, list) and msgs),
            'Datos inválidos'
        )
        return jsonify({'error': first_error}), 400

    cart_col = current_app.config['CART_ITEMS_COLLECTION']
    products_col = current_app.config['PRODUCTS_COLLECTION']

    # Ensure cart item belongs to the current user
    cart_item = cart_col.find_one({'_id': item_oid, 'user_id': user_oid})
    if not cart_item:
        return jsonify({'error': 'Elemento del carrito no encontrado'}), 404

    quantity = validated['quantity']

    if quantity <= 0:
        cart_col.delete_one({'_id': item_oid})
    else:
        product = products_col.find_one({'_id': cart_item['product_id']})
        if product and product['stock'] < quantity:
            return jsonify({'error': 'No hay suficiente stock'}), 400
        cart_col.update_one(
            {'_id': item_oid},
            {'$set': {'quantity': quantity}}
        )

    return jsonify({'message': 'Carrito actualizado'}), 200


@cart_bp.route('/<item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove an item from the cart."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    item_oid = to_object_id(item_id)

    if not user_oid or not item_oid:
        return jsonify({'error': 'ID inválido'}), 400

    cart_col = current_app.config['CART_ITEMS_COLLECTION']

    # Only delete if it belongs to the current user
    result = cart_col.delete_one({'_id': item_oid, 'user_id': user_oid})
    if result.deleted_count == 0:
        return jsonify({'error': 'Elemento del carrito no encontrado'}), 404

    return jsonify({'message': 'Elemento eliminado del carrito'}), 200


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from the cart."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    if not user_oid:
        return jsonify({'error': 'ID de usuario inválido'}), 400

    cart_col = current_app.config['CART_ITEMS_COLLECTION']
    cart_col.delete_many({'user_id': user_oid})

    return jsonify({'message': 'Carrito vaciado'}), 200
