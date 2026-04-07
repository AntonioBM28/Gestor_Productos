"""Product routes for Gestor de Productos.

Public read access, admin-only write access. All inputs sanitized
and validated with Marshmallow schemas. Search protected against
NoSQL/regex injection.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from models import (
    serialize_product, to_object_id,
    ProductCreateSchema, ProductSchema
)
from middleware import admin_required
from security import sanitize_string, escape_regex, log_security_event
from datetime import datetime, timezone

products_bp = Blueprint('products', __name__)

# Schema instances
_create_schema = ProductCreateSchema()
_update_schema = ProductSchema()


@products_bp.route('', methods=['GET'])
def get_products():
    """Get all products (public access)."""
    from app import limiter
    limiter.limit('60/minute')(lambda: None)()

    products_col = current_app.config['PRODUCTS_COLLECTION']

    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()

    query_filter = {}

    if category:
        # Sanitize and use exact match (no regex)
        query_filter['category'] = sanitize_string(category, max_length=100)

    if search:
        # ⚠️ CRITICAL: Escape regex special characters to prevent injection
        safe_search = escape_regex(sanitize_string(search, max_length=100))
        query_filter['name'] = {'$regex': safe_search, '$options': 'i'}

    products = list(
        products_col.find(query_filter).sort('created_at', -1)
    )

    return jsonify({'products': [serialize_product(p) for p in products]}), 200


@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID (public access)."""
    products_col = current_app.config['PRODUCTS_COLLECTION']

    oid = to_object_id(product_id)
    if not oid:
        return jsonify({'error': 'ID de producto inválido'}), 400

    product = products_col.find_one({'_id': oid})
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404

    return jsonify({'product': serialize_product(product)}), 200


@products_bp.route('', methods=['POST'])
@admin_required
def create_product():
    """Create a new product (admin only)."""
    from app import limiter
    limiter.limit('10/minute')(lambda: None)()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # Validate with Marshmallow
    try:
        validated = _create_schema.load(data)
    except ValidationError as e:
        first_error = next(
            (msgs[0] for msgs in e.messages.values() if isinstance(msgs, list) and msgs),
            'Datos inválidos'
        )
        return jsonify({'error': first_error}), 400

    products_col = current_app.config['PRODUCTS_COLLECTION']
    now = datetime.now(timezone.utc)

    product_doc = {
        'name': validated['name'],
        'description': validated.get('description', ''),
        'price': float(validated['price']),
        'stock': int(validated.get('stock', 0)),
        'image_url': validated.get('image_url', ''),
        'category': validated.get('category', ''),
        'created_at': now,
        'updated_at': now
    }

    result = products_col.insert_one(product_doc)
    product_doc['_id'] = result.inserted_id

    user_id = get_jwt_identity()
    log_security_event(
        'PRODUCT_CREATED',
        f'name={product_doc["name"]} id={result.inserted_id}',
        user_id
    )

    return jsonify({
        'message': 'Producto creado exitosamente',
        'product': serialize_product(product_doc)
    }), 201


@products_bp.route('/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update a product (admin only)."""
    from app import limiter
    limiter.limit('10/minute')(lambda: None)()

    products_col = current_app.config['PRODUCTS_COLLECTION']

    oid = to_object_id(product_id)
    if not oid:
        return jsonify({'error': 'ID de producto inválido'}), 400

    product = products_col.find_one({'_id': oid})
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # Validate with schema (partial update)
    try:
        validated = _update_schema.load(data, partial=True)
    except ValidationError as e:
        first_error = next(
            (msgs[0] for msgs in e.messages.values() if isinstance(msgs, list) and msgs),
            'Datos inválidos'
        )
        return jsonify({'error': first_error}), 400

    update_fields = {'updated_at': datetime.now(timezone.utc)}

    if 'name' in validated:
        update_fields['name'] = validated['name']
    if 'description' in validated:
        update_fields['description'] = validated['description']
    if 'price' in validated:
        update_fields['price'] = float(validated['price'])
    if 'stock' in validated:
        update_fields['stock'] = int(validated['stock'])
    if 'image_url' in validated:
        update_fields['image_url'] = validated['image_url']
    if 'category' in validated:
        update_fields['category'] = validated['category']

    products_col.update_one({'_id': oid}, {'$set': update_fields})

    updated_product = products_col.find_one({'_id': oid})

    user_id = get_jwt_identity()
    log_security_event('PRODUCT_UPDATED', f'id={product_id}', user_id)

    return jsonify({
        'message': 'Producto actualizado exitosamente',
        'product': serialize_product(updated_product)
    }), 200


@products_bp.route('/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete a product (admin only)."""
    products_col = current_app.config['PRODUCTS_COLLECTION']

    oid = to_object_id(product_id)
    if not oid:
        return jsonify({'error': 'ID de producto inválido'}), 400

    product = products_col.find_one({'_id': oid})
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404

    products_col.delete_one({'_id': oid})

    user_id = get_jwt_identity()
    log_security_event(
        'PRODUCT_DELETED',
        f'name={product.get("name")} id={product_id}',
        user_id
    )

    return jsonify({'message': 'Producto eliminado exitosamente'}), 200


@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all unique categories."""
    products_col = current_app.config['PRODUCTS_COLLECTION']

    categories = products_col.distinct('category', {
        'category': {'$ne': None, '$ne': ''}
    })

    # Filter out empty strings
    categories = [c for c in categories if c]

    return jsonify({'categories': categories}), 200
