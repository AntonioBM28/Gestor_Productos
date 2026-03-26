from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, CartItem, User
from middleware import admin_required
from utils import generate_reference_code, generate_qr_base64, generate_barcode_number
from datetime import datetime, timezone

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    """Create an order from the current cart with a payment reference code."""
    user_id = int(get_jwt_identity())

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    # Validate stock
    for item in cart_items:
        if not item.product:
            return jsonify({'error': f'Product not found for cart item {item.id}'}), 404
        if item.product.stock < item.quantity:
            return jsonify({
                'error': f'Not enough stock for {item.product.name}. Available: {item.product.stock}'
            }), 400

    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart_items)

    # Generate reference code
    reference_code = generate_reference_code()
    barcode_number = generate_barcode_number()

    # Create order
    order = Order(
        user_id=user_id,
        total=round(total, 2),
        status='pending',
        reference_code=reference_code
    )
    db.session.add(order)
    db.session.flush()

    # Create order items and update stock
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.product.price
        )
        db.session.add(order_item)
        item.product.stock -= item.quantity

    # Clear cart
    CartItem.query.filter_by(user_id=user_id).delete()

    db.session.commit()

    # Generate QR code
    qr_data = f"PAGO|REF:{reference_code}|TOTAL:{order.total}|BARCODE:{barcode_number}"
    qr_base64 = generate_qr_base64(qr_data)

    return jsonify({
        'message': 'Order created successfully',
        'order': order.to_dict(),
        'payment': {
            'reference_code': reference_code,
            'barcode_number': barcode_number,
            'qr_code': qr_base64,
            'total': order.total,
            'instructions': 'Presenta este código en cualquier tienda OXXO o punto de pago autorizado para completar tu compra.'
        }
    }), 201


@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get orders - users see their own, admins see all."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role == 'admin':
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    return jsonify({'orders': [o.to_dict() for o in orders]}), 200


@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a specific order."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if user.role != 'admin' and order.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    # Re-generate QR for viewing
    qr_data = f"PAGO|REF:{order.reference_code}|TOTAL:{order.total}"
    qr_base64 = generate_qr_base64(qr_data)

    order_data = order.to_dict()
    order_data['qr_code'] = qr_base64

    return jsonify({'order': order_data}), 200


@orders_bp.route('/<int:order_id>/confirm', methods=['PUT'])
@admin_required
def confirm_order(order_id):
    """Confirm payment received for an order (admin only)."""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if order.status == 'confirmed':
        return jsonify({'error': 'Order already confirmed'}), 400

    order.status = 'confirmed'
    order.confirmed_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'message': 'Payment confirmed',
        'order': order.to_dict()
    }), 200


@orders_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order and restore stock."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if user.role != 'admin' and order.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    if order.status == 'confirmed':
        return jsonify({'error': 'Cannot cancel a confirmed order'}), 400

    # Restore stock
    for item in order.items:
        if item.product:
            item.product.stock += item.quantity

    order.status = 'cancelled'
    db.session.commit()

    return jsonify({
        'message': 'Order cancelled',
        'order': order.to_dict()
    }), 200
