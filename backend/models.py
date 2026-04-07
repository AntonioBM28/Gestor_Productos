"""Serialization helpers and validators for MongoDB documents."""
from bson import ObjectId
from datetime import datetime, timezone


# ─── Serialization Helpers ────────────────────────────────────────────────────

def serialize_user(user):
    """Convert a MongoDB user document to a JSON-friendly dict."""
    if not user:
        return None
    return {
        'id': str(user['_id']),
        'username': user.get('username', ''),
        'email': user.get('email', ''),
        'role': user.get('role', 'user'),
        'created_at': user['created_at'].isoformat() if user.get('created_at') else None
    }


def serialize_product(product):
    """Convert a MongoDB product document to a JSON-friendly dict."""
    if not product:
        return None
    return {
        'id': str(product['_id']),
        'name': product.get('name', ''),
        'description': product.get('description', ''),
        'price': product.get('price', 0),
        'stock': product.get('stock', 0),
        'image_url': product.get('image_url', ''),
        'category': product.get('category', ''),
        'created_at': product['created_at'].isoformat() if product.get('created_at') else None,
        'updated_at': product['updated_at'].isoformat() if product.get('updated_at') else None
    }


def serialize_cart_item(cart_item, product=None):
    """Convert a MongoDB cart_item document to a JSON-friendly dict."""
    if not cart_item:
        return None
    result = {
        'id': str(cart_item['_id']),
        'user_id': str(cart_item.get('user_id', '')),
        'product_id': str(cart_item.get('product_id', '')),
        'quantity': cart_item.get('quantity', 1),
        'added_at': cart_item['added_at'].isoformat() if cart_item.get('added_at') else None
    }
    if product:
        result['product'] = serialize_product(product)
    return result


def serialize_order(order):
    """Convert a MongoDB order document to a JSON-friendly dict."""
    if not order:
        return None
    return {
        'id': str(order['_id']),
        'user_id': str(order.get('user_id', '')),
        'total': order.get('total', 0),
        'status': order.get('status', 'pending'),
        'reference_code': order.get('reference_code', ''),
        'items': order.get('items', []),
        'created_at': order['created_at'].isoformat() if order.get('created_at') else None,
        'confirmed_at': order['confirmed_at'].isoformat() if order.get('confirmed_at') else None
    }


# ─── Validation Helpers ──────────────────────────────────────────────────────

def validate_product_data(data, require_all=True):
    """Validate product data. Returns (is_valid, error_message)."""
    if require_all:
        if not data.get('name', '').strip():
            return False, 'Name is required'
        if data.get('price') is None:
            return False, 'Price is required'

    if 'price' in data and data['price'] is not None:
        try:
            price = float(data['price'])
            if price < 0:
                return False, 'Price must be positive'
        except (ValueError, TypeError):
            return False, 'Price must be a number'

    if 'stock' in data and data['stock'] is not None:
        try:
            stock = int(data['stock'])
            if stock < 0:
                return False, 'Stock must be non-negative'
        except (ValueError, TypeError):
            return False, 'Stock must be an integer'

    return True, None


def validate_user_data(data):
    """Validate user registration data. Returns (is_valid, error_message)."""
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return False, 'Username, email, and password are required'

    if len(password) < 6:
        return False, 'Password must be at least 6 characters'

    return True, None


def to_object_id(id_str):
    """Safely convert a string to ObjectId. Returns None if invalid."""
    try:
        return ObjectId(id_str)
    except Exception:
        return None
