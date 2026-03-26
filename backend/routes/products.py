from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Product
from middleware import admin_required

products_bp = Blueprint('products', __name__)


@products_bp.route('', methods=['GET'])
def get_products():
    """Get all products (public access)."""
    category = request.args.get('category')
    search = request.args.get('search')

    query = Product.query

    if category:
        query = query.filter_by(category=category)

    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    products = query.order_by(Product.created_at.desc()).all()
    return jsonify({'products': [p.to_dict() for p in products]}), 200


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID (public access)."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'product': product.to_dict()}), 200


@products_bp.route('', methods=['POST'])
@admin_required
def create_product():
    """Create a new product (admin only)."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    price = data.get('price')
    stock = data.get('stock', 0)

    if not name or price is None:
        return jsonify({'error': 'Name and price are required'}), 400

    if price < 0:
        return jsonify({'error': 'Price must be positive'}), 400

    product = Product(
        name=name,
        description=data.get('description', ''),
        price=float(price),
        stock=int(stock),
        image_url=data.get('image_url', ''),
        category=data.get('category', '')
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201


@products_bp.route('/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update a product (admin only)."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        product.name = data['name'].strip()
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        if data['price'] < 0:
            return jsonify({'error': 'Price must be positive'}), 400
        product.price = float(data['price'])
    if 'stock' in data:
        product.stock = int(data['stock'])
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'category' in data:
        product.category = data['category']

    db.session.commit()

    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    }), 200


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete a product (admin only)."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'}), 200


@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all unique categories."""
    categories = db.session.query(Product.category).distinct().filter(
        Product.category.isnot(None),
        Product.category != ''
    ).all()
    return jsonify({'categories': [c[0] for c in categories]}), 200
