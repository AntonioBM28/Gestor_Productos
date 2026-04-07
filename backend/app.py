import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from db import init_db
from datetime import timedelta


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})
    JWTManager(app)

    # Initialize MongoDB
    init_db(app)

    # Register blueprints
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

    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'ok', 'message': 'Gestor de Productos API running (MongoDB)'}, 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
