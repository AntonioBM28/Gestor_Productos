from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CartItem, Product
from middleware import user_required

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    """Get the current user's cart items."""
    user_id = int(get_jwt_identity())
    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    total = sum(
        item.product.price * item.quantity
        for item in cart_items if item.product
    )

    return jsonify({
        'items': [item.to_dict() for item in cart_items],
        'total': round(total, 2),
        'count': len(cart_items)
    }), 200


@cart_bp.route('', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add a product to the cart."""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if product.stock < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400

    # Check if product already in cart
    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        new_qty = existing.quantity + quantity
        if product.stock < new_qty:
            return jsonify({'error': 'Not enough stock available'}), 400
        existing.quantity = new_qty
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({'message': 'Product added to cart'}), 201


@cart_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity."""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404

    quantity = data.get('quantity', 1)
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        if cart_item.product.stock < quantity:
            return jsonify({'error': 'Not enough stock'}), 400
        cart_item.quantity = quantity

    db.session.commit()
    return jsonify({'message': 'Cart updated'}), 200


@cart_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove an item from the cart."""
    user_id = int(get_jwt_identity())

    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({'message': 'Item removed from cart'}), 200


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from the cart."""
    user_id = int(get_jwt_identity())
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'message': 'Cart cleared'}), 200
