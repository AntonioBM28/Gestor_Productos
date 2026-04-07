from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import serialize_order, to_object_id
from middleware import admin_required
from utils import generate_reference_code, generate_qr_base64, generate_barcode_number
from datetime import datetime, timezone

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    """Create an order from the current cart with a payment reference code."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    if not user_oid:
        return jsonify({'error': 'Invalid user ID'}), 400

    cart_col = current_app.config['CART_ITEMS_COLLECTION']
    products_col = current_app.config['PRODUCTS_COLLECTION']
    orders_col = current_app.config['ORDERS_COLLECTION']

    cart_items = list(cart_col.find({'user_id': user_oid}))
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    # Validate stock and calculate total
    total = 0.0
    order_items = []

    for item in cart_items:
        product = products_col.find_one({'_id': item['product_id']})
        if not product:
            return jsonify({'error': f'Product not found for cart item'}), 404
        if product['stock'] < item['quantity']:
            return jsonify({
                'error': f'Not enough stock for {product["name"]}. Available: {product["stock"]}'
            }), 400

        total += product['price'] * item['quantity']
        order_items.append({
            'product_id': str(item['product_id']),
            'product_name': product['name'],
            'quantity': item['quantity'],
            'price_at_purchase': product['price']
        })

    # Generate reference code
    reference_code = generate_reference_code()
    barcode_number = generate_barcode_number()

    now = datetime.now(timezone.utc)

    # Create order document
    order_doc = {
        'user_id': user_oid,
        'total': round(total, 2),
        'status': 'pending',
        'reference_code': reference_code,
        'items': order_items,
        'created_at': now,
        'confirmed_at': None
    }

    result = orders_col.insert_one(order_doc)
    order_doc['_id'] = result.inserted_id

    # Update stock for each product
    for item in cart_items:
        products_col.update_one(
            {'_id': item['product_id']},
            {'$inc': {'stock': -item['quantity']}}
        )

    # Clear cart
    cart_col.delete_many({'user_id': user_oid})

    # Generate QR code
    qr_data = f"PAGO|REF:{reference_code}|TOTAL:{order_doc['total']}|BARCODE:{barcode_number}"
    qr_base64 = generate_qr_base64(qr_data)

    return jsonify({
        'message': 'Order created successfully',
        'order': serialize_order(order_doc),
        'payment': {
            'reference_code': reference_code,
            'barcode_number': barcode_number,
            'qr_code': qr_base64,
            'total': order_doc['total'],
            'instructions': 'Presenta este código en cualquier tienda OXXO o punto de pago autorizado para completar tu compra.'
        }
    }), 201


@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get orders - users see their own, admins see all."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    if not user_oid:
        return jsonify({'error': 'Invalid user ID'}), 400

    users_col = current_app.config['USERS_COLLECTION']
    orders_col = current_app.config['ORDERS_COLLECTION']

    user = users_col.find_one({'_id': user_oid})

    if user and user.get('role') == 'admin':
        orders = list(orders_col.find().sort('created_at', -1))
    else:
        orders = list(orders_col.find({'user_id': user_oid}).sort('created_at', -1))

    return jsonify({'orders': [serialize_order(o) for o in orders]}), 200


@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a specific order."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    order_oid = to_object_id(order_id)

    if not user_oid or not order_oid:
        return jsonify({'error': 'Invalid ID'}), 400

    users_col = current_app.config['USERS_COLLECTION']
    orders_col = current_app.config['ORDERS_COLLECTION']

    user = users_col.find_one({'_id': user_oid})
    order = orders_col.find_one({'_id': order_oid})

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if user.get('role') != 'admin' and order['user_id'] != user_oid:
        return jsonify({'error': 'Access denied'}), 403

    # Re-generate QR for viewing
    qr_data = f"PAGO|REF:{order['reference_code']}|TOTAL:{order['total']}"
    qr_base64 = generate_qr_base64(qr_data)

    order_data = serialize_order(order)
    order_data['qr_code'] = qr_base64

    return jsonify({'order': order_data}), 200


@orders_bp.route('/<order_id>/confirm', methods=['PUT'])
@admin_required
def confirm_order(order_id):
    """Confirm payment received for an order (admin only)."""
    order_oid = to_object_id(order_id)
    if not order_oid:
        return jsonify({'error': 'Invalid order ID'}), 400

    orders_col = current_app.config['ORDERS_COLLECTION']

    order = orders_col.find_one({'_id': order_oid})
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if order['status'] == 'confirmed':
        return jsonify({'error': 'Order already confirmed'}), 400

    orders_col.update_one(
        {'_id': order_oid},
        {'$set': {
            'status': 'confirmed',
            'confirmed_at': datetime.now(timezone.utc)
        }}
    )

    updated_order = orders_col.find_one({'_id': order_oid})

    return jsonify({
        'message': 'Payment confirmed',
        'order': serialize_order(updated_order)
    }), 200


@orders_bp.route('/<order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order and restore stock."""
    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    order_oid = to_object_id(order_id)

    if not user_oid or not order_oid:
        return jsonify({'error': 'Invalid ID'}), 400

    users_col = current_app.config['USERS_COLLECTION']
    orders_col = current_app.config['ORDERS_COLLECTION']
    products_col = current_app.config['PRODUCTS_COLLECTION']

    user = users_col.find_one({'_id': user_oid})
    order = orders_col.find_one({'_id': order_oid})

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if user.get('role') != 'admin' and order['user_id'] != user_oid:
        return jsonify({'error': 'Access denied'}), 403

    if order['status'] == 'confirmed':
        return jsonify({'error': 'Cannot cancel a confirmed order'}), 400

    # Restore stock
    for item in order.get('items', []):
        product_oid = to_object_id(item['product_id'])
        if product_oid:
            products_col.update_one(
                {'_id': product_oid},
                {'$inc': {'stock': item['quantity']}}
            )

    orders_col.update_one(
        {'_id': order_oid},
        {'$set': {'status': 'cancelled'}}
    )

    updated_order = orders_col.find_one({'_id': order_oid})

    return jsonify({
        'message': 'Order cancelled',
        'order': serialize_order(updated_order)
    }), 200
