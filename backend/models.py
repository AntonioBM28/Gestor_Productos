"""Serialization helpers, schemas and validators for MongoDB documents."""
import re
from bson import ObjectId
from datetime import datetime, timezone
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load
from security import sanitize_string


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
        'is_active': user.get('is_active', True),
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


# ─── ObjectId Helper ─────────────────────────────────────────────────────────

def to_object_id(id_str):
    """Safely convert a string to ObjectId. Returns None if invalid."""
    try:
        return ObjectId(id_str)
    except Exception:
        return None


# ─── Marshmallow Schemas ─────────────────────────────────────────────────────

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_.-]{3,30}$')


class UserRegistrationSchema(Schema):
    """Schema for user registration validation."""
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=30)
    )
    email = fields.String(
        required=True,
        validate=validate.Length(min=5, max=120)
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=128),
        load_only=True
    )

    @pre_load
    def strip_fields(self, data, **kwargs):
        """Strip whitespace from string fields."""
        if 'username' in data and isinstance(data['username'], str):
            data['username'] = sanitize_string(data['username'], max_length=30)
        if 'email' in data and isinstance(data['email'], str):
            data['email'] = data['email'].strip().lower()[:120]
        return data

    @validates('username')
    def validate_username(self, value, **kwargs):
        if not USERNAME_REGEX.match(value):
            raise ValidationError(
                'El nombre de usuario solo puede contener letras, números, '
                'guiones, puntos y guiones bajos (3-30 caracteres)'
            )

    @validates('email')
    def validate_email(self, value, **kwargs):
        if not EMAIL_REGEX.match(value):
            raise ValidationError('Formato de email inválido')


class UserLoginSchema(Schema):
    """Schema for user login validation."""
    email = fields.String(required=True, validate=validate.Length(min=1, max=120))
    password = fields.String(required=True, validate=validate.Length(min=1, max=128))

    @pre_load
    def strip_fields(self, data, **kwargs):
        if 'email' in data and isinstance(data['email'], str):
            data['email'] = data['email'].strip().lower()[:120]
        return data


class ChangePasswordSchema(Schema):
    """Schema for password change validation."""
    current_password = fields.String(required=True, validate=validate.Length(min=1, max=128))
    new_password = fields.String(required=True, validate=validate.Length(min=8, max=128))


class ProductSchema(Schema):
    """Schema for product creation/update validation."""
    name = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(validate=validate.Length(max=2000), load_default='')
    price = fields.Float(validate=validate.Range(min=0.01, max=1_000_000))
    stock = fields.Integer(validate=validate.Range(min=0, max=99_999), load_default=0)
    image_url = fields.String(validate=validate.Length(max=500), load_default='')
    category = fields.String(validate=validate.Length(max=100), load_default='')

    @pre_load
    def sanitize_fields(self, data, **kwargs):
        """Sanitize string fields."""
        if 'name' in data and isinstance(data['name'], str):
            data['name'] = sanitize_string(data['name'], max_length=200)
        if 'description' in data and isinstance(data['description'], str):
            data['description'] = sanitize_string(data['description'], max_length=2000)
        if 'category' in data and isinstance(data['category'], str):
            data['category'] = sanitize_string(data['category'], max_length=100)
        if 'image_url' in data and isinstance(data['image_url'], str):
            data['image_url'] = data['image_url'].strip()[:500]
        return data


class ProductCreateSchema(ProductSchema):
    """Schema for product creation — name and price are required."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    price = fields.Float(required=True, validate=validate.Range(min=0.01, max=1_000_000))


class CartItemSchema(Schema):
    """Schema for adding/updating cart items."""
    product_id = fields.String(required=True, validate=validate.Length(min=1, max=50))
    quantity = fields.Integer(
        validate=validate.Range(min=1, max=100),
        load_default=1
    )


class CartUpdateSchema(Schema):
    """Schema for updating cart item quantity."""
    quantity = fields.Integer(
        required=True,
        validate=validate.Range(min=0, max=100)
    )


class RoleUpdateSchema(Schema):
    """Schema for updating user role."""
    role = fields.String(
        required=True,
        validate=validate.OneOf(['user', 'admin'])
    )

    @pre_load
    def strip_role(self, data, **kwargs):
        if 'role' in data and isinstance(data['role'], str):
            data['role'] = data['role'].strip().lower()
        return data


# ─── Legacy Validation (kept for backward compatibility) ─────────────────────

def validate_product_data(data, require_all=True):
    """Validate product data using Marshmallow schema.

    Returns (is_valid, error_message).
    """
    try:
        schema = ProductCreateSchema() if require_all else ProductSchema()
        schema.load(data)
        return True, None
    except ValidationError as e:
        # Get the first error message
        for field_errors in e.messages.values():
            if isinstance(field_errors, list) and field_errors:
                return False, field_errors[0]
        return False, 'Datos inválidos'


def validate_user_data(data):
    """Validate user registration data using Marshmallow schema.

    Returns (is_valid, error_message).
    """
    try:
        UserRegistrationSchema().load(data)
        return True, None
    except ValidationError as e:
        for field_errors in e.messages.values():
            if isinstance(field_errors, list) and field_errors:
                return False, field_errors[0]
        return False, 'Datos inválidos'
