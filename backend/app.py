"""Flask application factory for Gestor de Productos.

Integrates security headers, rate limiting, JWT blacklist, and CORS.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import get_config
from db import init_db
from security import add_security_headers, log_security_event

# Global limiter instance (shared across blueprints)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri='memory://',
    default_limits=[]
)


def create_app():
    app = Flask(__name__)

    # ── Load Configuration ────────────────────────────────────────────────
    config = get_config()
    app.config.from_object(config)

    # Enforce max request body size
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

    # ── Initialize Extensions ─────────────────────────────────────────────

    # CORS — only allow specified origins
    CORS(app, resources={r"/api/*": {
        "origins": config.CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["X-RateLimit-Remaining", "X-RateLimit-Limit"],
        "max_age": 600
    }})

    # JWT
    jwt = JWTManager(app)

    # Rate Limiter
    limiter.init_app(app)

    # MongoDB
    init_db(app)

    # ── JWT Callbacks ─────────────────────────────────────────────────────

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if a JWT token has been revoked (blacklisted)."""
        jti = jwt_payload['jti']
        blacklist = app.config.get('TOKEN_BLACKLIST_COLLECTION')
        if blacklist is None:
            return False
        token = blacklist.find_one({'jti': jti})
        return token is not None

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token expirado. Por favor inicia sesión de nuevo'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Token inválido'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Token de autorización requerido'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token revocado. Por favor inicia sesión de nuevo'
        }), 401

    # ── Security Headers ──────────────────────────────────────────────────

    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)

    # ── Global Error Handlers ─────────────────────────────────────────────

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'error': 'El cuerpo de la solicitud es demasiado grande (máx 2MB)'
        }), 413

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'error': 'Demasiadas solicitudes. Intenta de nuevo más tarde'
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        # Log but don't expose internal details
        log_security_event('INTERNAL_ERROR', str(error), level='error')
        return jsonify({
            'error': 'Error interno del servidor'
        }), 500

    # ── Register Blueprints ───────────────────────────────────────────────
    from auth import auth_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    # ── Health Check ──────────────────────────────────────────────────────

    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'ok', 'message': 'Gestor de Productos API running (MongoDB)'}, 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
