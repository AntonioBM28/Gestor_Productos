from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import serialize_product, validate_product_data, to_object_id
from middleware import admin_required
from datetime import datetime, timezone

products_bp = Blueprint('products', __name__)


@products_bp.route('', methods=['GET'])
def get_products():
    """Get all products (public access)."""
    products_col = current_app.config['PRODUCTS_COLLECTION']

    category = request.args.get('category')
    search = request.args.get('search')

    query_filter = {}

    if category:
        query_filter['category'] = category

    if search:
        query_filter['name'] = {'$regex': search, '$options': 'i'}

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
        return jsonify({'error': 'Invalid product ID'}), 400

    product = products_col.find_one({'_id': oid})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify({'product': serialize_product(product)}), 200


@products_bp.route('', methods=['POST'])
@admin_required
def create_product():
    """Create a new product (admin only)."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    is_valid, error = validate_product_data(data, require_all=True)
    if not is_valid:
        return jsonify({'error': error}), 400

    products_col = current_app.config['PRODUCTS_COLLECTION']
    now = datetime.now(timezone.utc)

    product_doc = {
        'name': data['name'].strip(),
        'description': data.get('description', ''),
        'price': float(data['price']),
        'stock': int(data.get('stock', 0)),
        'image_url': data.get('image_url', ''),
        'category': data.get('category', ''),
        'created_at': now,
        'updated_at': now
    }

    result = products_col.insert_one(product_doc)
    product_doc['_id'] = result.inserted_id

    return jsonify({
        'message': 'Product created successfully',
        'product': serialize_product(product_doc)
    }), 201


@products_bp.route('/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update a product (admin only)."""
    products_col = current_app.config['PRODUCTS_COLLECTION']

    oid = to_object_id(product_id)
    if not oid:
        return jsonify({'error': 'Invalid product ID'}), 400

    product = products_col.find_one({'_id': oid})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    is_valid, error = validate_product_data(data, require_all=False)
    if not is_valid:
        return jsonify({'error': error}), 400

    update_fields = {'updated_at': datetime.now(timezone.utc)}

    if 'name' in data:
        update_fields['name'] = data['name'].strip()
    if 'description' in data:
        update_fields['description'] = data['description']
    if 'price' in data:
        update_fields['price'] = float(data['price'])
    if 'stock' in data:
        update_fields['stock'] = int(data['stock'])
    if 'image_url' in data:
        update_fields['image_url'] = data['image_url']
    if 'category' in data:
        update_fields['category'] = data['category']

    products_col.update_one({'_id': oid}, {'$set': update_fields})

    updated_product = products_col.find_one({'_id': oid})

    return jsonify({
        'message': 'Product updated successfully',
        'product': serialize_product(updated_product)
    }), 200


@products_bp.route('/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete a product (admin only)."""
    products_col = current_app.config['PRODUCTS_COLLECTION']

    oid = to_object_id(product_id)
    if not oid:
        return jsonify({'error': 'Invalid product ID'}), 400

    product = products_col.find_one({'_id': oid})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    products_col.delete_one({'_id': oid})

    return jsonify({'message': 'Product deleted successfully'}), 200


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
