"""Centralized configuration for Gestor de Productos backend."""
import os
import secrets
from datetime import timedelta


class Config:
    """Base configuration."""

    # ── Flask Core ────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)

    # ── JWT Tokens ────────────────────────────────────────────────────────
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ERROR_MESSAGE_KEY = 'error'

    # ── MongoDB ───────────────────────────────────────────────────────────
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'gestor_productos')

    # ── Rate Limiting ─────────────────────────────────────────────────────
    RATELIMIT_DEFAULT = os.environ.get('RATE_LIMIT_DEFAULT', '200/hour')
    RATELIMIT_STORAGE_URI = 'memory://'

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS = os.environ.get(
        'CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000'
    ).split(',')

    # ── Security Policies ─────────────────────────────────────────────────
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB max request body
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_MINUTES = 15
    MAX_CART_ITEMS = 50
    MAX_CART_QUANTITY = 100
    MAX_PRODUCT_PRICE = 1_000_000
    MAX_PRODUCT_STOCK = 99_999


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Longer for dev convenience


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

    @classmethod
    def init_app(cls):
        """Validate critical settings for production."""
        if os.environ.get('SECRET_KEY') in (None, 'dev-secret-key-change-in-production'):
            raise ValueError(
                '❌ SECRET_KEY must be set to a secure value in production! '
                'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        if os.environ.get('JWT_SECRET_KEY') in (None, 'jwt-secret-key-change-in-production'):
            raise ValueError(
                '❌ JWT_SECRET_KEY must be set to a secure value in production!'
            )


# Configuration map
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get the configuration class based on FLASK_ENV."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default'])
