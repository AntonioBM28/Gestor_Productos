"""MongoDB connection module for Gestor de Productos."""
from pymongo import MongoClient, ASCENDING, DESCENDING
import os


# MongoDB configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'gestor_productos')

# Global client and database references
_client = None
_db = None


def get_db():
    """Get the MongoDB database instance."""
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _db = _client[MONGO_DB_NAME]
    return _db


def init_db(app):
    """Initialize MongoDB connection and store references in the Flask app."""
    db = get_db()

    # Store database and collection references in app config
    app.config['MONGO_DB'] = db
    app.config['USERS_COLLECTION'] = db['users']
    app.config['PRODUCTS_COLLECTION'] = db['products']
    app.config['CART_ITEMS_COLLECTION'] = db['cart_items']
    app.config['ORDERS_COLLECTION'] = db['orders']
    app.config['TOKEN_BLACKLIST_COLLECTION'] = db['token_blacklist']

    # ── Indexes ───────────────────────────────────────────────────────────

    # Users
    db['users'].create_index([('email', ASCENDING)], unique=True)
    db['users'].create_index([('username', ASCENDING)], unique=True)
    db['users'].create_index([('is_active', ASCENDING)])

    # Products
    db['products'].create_index([('name', ASCENDING)])
    db['products'].create_index([('category', ASCENDING)])

    # Cart
    db['cart_items'].create_index([('user_id', ASCENDING)])
    db['cart_items'].create_index(
        [('user_id', ASCENDING), ('product_id', ASCENDING)],
        unique=True
    )

    # Orders
    db['orders'].create_index([('user_id', ASCENDING)])
    db['orders'].create_index([('reference_code', ASCENDING)], unique=True)
    db['orders'].create_index([('created_at', DESCENDING)])

    # Token blacklist — TTL index auto-deletes expired tokens after 31 days
    db['token_blacklist'].create_index(
        [('created_at', ASCENDING)],
        expireAfterSeconds=31 * 24 * 3600  # 31 days
    )
    db['token_blacklist'].create_index([('jti', ASCENDING)], unique=True)

    # Security logs — TTL index auto-deletes after 90 days
    db['security_logs'].create_index(
        [('timestamp', ASCENDING)],
        expireAfterSeconds=90 * 24 * 3600  # 90 days
    )
    db['security_logs'].create_index([('event_type', ASCENDING)])
    db['security_logs'].create_index([('ip_address', ASCENDING)])

    return db


def close_db():
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
