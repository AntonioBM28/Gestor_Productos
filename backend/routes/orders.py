"""Order routes for Gestor de Productos.

Handles checkout, order listing, order details, payment confirmation,
and cancellation. All operations are rate-limited and logged.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import serialize_order, to_object_id
from middleware import admin_required
from utils import generate_reference_code, generate_qr_base64, generate_barcode_number
from security import log_security_event
from datetime import datetime, timezone

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    """Create an order from the current cart with a payment reference code."""
    from app import limiter
    limiter.limit('5/minute')(lambda: None)()

    user_id = get_jwt_identity()
    user_oid = to_object_id(user_id)
    if not user_oid:
        return jsonify({'error': 'ID de usuario inválido'}), 400

    # Verify user is active
    users_col = current_app.config['USERS_COLLECTION']
    user = users_col.find_one({'_id': user_oid})
    if not user or not user.get('is_active', True):
        return jsonify({'error': 'Cuenta no activa'}), 403

    cart_col = current_app.config['CART_ITEMS_COLLECTION']
    products_col = current_app.config['PRODUCTS_COLLECTION']
    orders_col = current_app.config['ORDERS_COLLECTION']

    cart_items = list(cart_col.find({'user_id': user_oid}))
    if not cart_items:
        return jsonify({'error': 'El carrito está vacío'}), 400

    # Validate stock and calculate total
    total = 0.0
    order_items = []

    for item in cart_items:
        product = products_col.find_one({'_id': item['product_id']})
        if not product:
            return jsonify({'error': 'Producto no encontrado en el carrito'}), 404
        if product['stock'] < item['quantity']:
            return jsonify({
                'error': f'No hay suficiente stock para {product["name"]}. Disponible: {product["stock"]}'
            }), 400

        item_total = product['price'] * item['quantity']
        total += item_total
        order_items.append({
            'product_id': str(item['product_id']),
            'product_name': product['name'],
            'quantity': item['quantity'],
            'price_at_purchase': product['price']
        })

    # Safety check: ensure total is reasonable
    if total <= 0 or total > 10_000_000:
        log_security_event(
            'CHECKOUT_SUSPICIOUS',
            f'total={total}',
            user_id,
            level='warning'
        )
        return jsonify({'error': 'Total de orden inválido'}), 400

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

    log_security_event(
        'ORDER_CREATED',
        f'order_id={result.inserted_id} total={order_doc["total"]} ref={reference_code}',
        user_id
    )

    return jsonify({
        'message': 'Orden creada exitosamente',
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
        return jsonify({'error': 'ID de usuario inválido'}), 400

    users_col = current_app.config['USERS_COLLECTION']
    orders_col = current_app.config['ORDERS_COLLECTION']

    user = users_col.find_one({'_id': user_oid})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    if user.get('role') == 'admin':
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
        return jsonify({'error': 'ID inválido'}), 400

    users_col = current_app.config['USERS_COLLECTION']
    orders_col = current_app.config['ORDERS_COLLECTION']

    user = users_col.find_one({'_id': user_oid})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    order = orders_col.find_one({'_id': order_oid})
    if not order:
        return jsonify({'error': 'Orden no encontrada'}), 404

    # Authorization: user can only see their own orders, admin can see all
    if user.get('role') != 'admin' and order['user_id'] != user_oid:
        log_security_event(
            'UNAUTHORIZED_ORDER_ACCESS',
            f'order_id={order_id}',
            user_id,
            level='warning'
        )
        return jsonify({'error': 'Acceso denegado'}), 403

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
        return jsonify({'error': 'ID de orden inválido'}), 400

    orders_col = current_app.config['ORDERS_COLLECTION']

    order = orders_col.find_one({'_id': order_oid})
    if not order:
        return jsonify({'error': 'Orden no encontrada'}), 404

    if order['status'] == 'confirmed':
        return jsonify({'error': 'La orden ya fue confirmada'}), 400

    if order['status'] == 'cancelled':
        return jsonify({'error': 'No se puede confirmar una orden cancelada'}), 400

    orders_col.update_one(
        {'_id': order_oid},
        {'$set': {
            'status': 'confirmed',
            'confirmed_at': datetime.now(timezone.utc)
        }}
    )

    updated_order = orders_col.find_one({'_id': order_oid})

    admin_id = get_jwt_identity()
    log_security_event(
        'ORDER_CONFIRMED',
        f'order_id={order_id} total={order.get("total")}',
        admin_id
    )

    return jsonify({
        'message': 'Pago confirmado',
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
        return jsonify({'error': 'ID inválido'}), 400

    users_col = current_app.config['USERS_COLLECTION']
    orders_col = current_app.config['ORDERS_COLLECTION']
    products_col = current_app.config['PRODUCTS_COLLECTION']

    user = users_col.find_one({'_id': user_oid})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    order = orders_col.find_one({'_id': order_oid})
    if not order:
        return jsonify({'error': 'Orden no encontrada'}), 404

    # Authorization check
    if user.get('role') != 'admin' and order['user_id'] != user_oid:
        log_security_event(
            'UNAUTHORIZED_ORDER_CANCEL',
            f'order_id={order_id}',
            user_id,
            level='warning'
        )
        return jsonify({'error': 'Acceso denegado'}), 403

    if order['status'] == 'confirmed':
        return jsonify({'error': 'No se puede cancelar una orden confirmada'}), 400

    if order['status'] == 'cancelled':
        return jsonify({'error': 'La orden ya fue cancelada'}), 400

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

    log_security_event(
        'ORDER_CANCELLED',
        f'order_id={order_id} by_user={user_id}',
        user_id
    )

    return jsonify({
        'message': 'Orden cancelada',
        'order': serialize_order(updated_order)
    }), 200
