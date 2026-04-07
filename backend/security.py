"""Security utilities for Gestor de Productos backend.

Includes HTTP security headers, input sanitization, NoSQL injection prevention,
password strength validation, and security event logging.
"""
import re
import logging
import bleach
from datetime import datetime, timezone
from flask import current_app, request

# ─── Security Logger ─────────────────────────────────────────────────────────

security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] SECURITY %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
security_logger.addHandler(_handler)


# ─── HTTP Security Headers ───────────────────────────────────────────────────

def add_security_headers(response):
    """Add security headers to every HTTP response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

    # Remove server header to avoid fingerprinting
    response.headers.pop('Server', None)

    return response


# ─── Input Sanitization ──────────────────────────────────────────────────────

# Characters that have special meaning in MongoDB query operators
_MONGO_OPERATORS = re.compile(r'^\$|\.\.|\0')


def sanitize_string(value, max_length=500):
    """Sanitize a string input: strip HTML, limit length, remove null bytes."""
    if not isinstance(value, str):
        return ''

    # Strip HTML tags and dangerous content
    cleaned = bleach.clean(value, tags=[], strip=True)

    # Remove null bytes
    cleaned = cleaned.replace('\x00', '')

    # Trim to max length
    cleaned = cleaned[:max_length]

    return cleaned.strip()


def sanitize_mongo_query(value):
    """Sanitize a value to prevent NoSQL injection.

    Prevents $-prefixed operators and other MongoDB injection vectors.
    """
    if isinstance(value, dict):
        # Reject any dict with $-prefixed keys (operator injection)
        sanitized = {}
        for key, val in value.items():
            if key.startswith('$'):
                security_logger.warning(
                    f'NoSQL injection attempt blocked: key={key} '
                    f'from IP={_get_client_ip()}'
                )
                continue  # Skip operator keys
            sanitized[key] = sanitize_mongo_query(val)
        return sanitized

    if isinstance(value, str):
        # Remove null bytes
        value = value.replace('\x00', '')
        # Check for operator injection in string values
        if _MONGO_OPERATORS.search(value):
            security_logger.warning(
                f'NoSQL injection attempt blocked: value starts with $ '
                f'from IP={_get_client_ip()}'
            )
            return ''
        return value

    if isinstance(value, list):
        return [sanitize_mongo_query(item) for item in value]

    return value


def escape_regex(pattern):
    """Escape special regex characters in a search pattern.

    Prevents regex injection via MongoDB $regex queries.
    """
    return re.escape(pattern) if isinstance(pattern, str) else ''


# ─── Password Strength Validation ────────────────────────────────────────────

def validate_password_strength(password):
    """Validate password meets security requirements.

    Requirements:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character

    Returns (is_valid, error_message).
    """
    if not password or not isinstance(password, str):
        return False, 'La contraseña es obligatoria'

    min_length = current_app.config.get('PASSWORD_MIN_LENGTH', 8)

    if len(password) < min_length:
        return False, f'La contraseña debe tener al menos {min_length} caracteres'

    if not re.search(r'[A-Z]', password):
        return False, 'La contraseña debe tener al menos 1 letra mayúscula'

    if not re.search(r'[a-z]', password):
        return False, 'La contraseña debe tener al menos 1 letra minúscula'

    if not re.search(r'\d', password):
        return False, 'La contraseña debe tener al menos 1 número'

    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return False, 'La contraseña debe tener al menos 1 carácter especial (!@#$%^&*...)'

    return True, None


# ─── Security Event Logging ──────────────────────────────────────────────────

def _get_client_ip():
    """Get the real client IP, considering proxy headers."""
    # Check X-Forwarded-For but don't blindly trust it
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        # Take the first IP (client) but only if behind a trusted proxy
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def log_security_event(event_type, details='', user_id=None, level='info'):
    """Log a security event with consistent formatting.

    Args:
        event_type: Type of event (LOGIN_SUCCESS, LOGIN_FAILED, etc.)
        details: Additional details
        user_id: User ID if applicable
        level: Log level (info, warning, error)
    """
    ip = _get_client_ip()
    user_agent = request.headers.get('User-Agent', 'unknown')[:200]
    msg = f'[{event_type}] IP={ip} User={user_id or "anonymous"} UA={user_agent} {details}'

    log_fn = getattr(security_logger, level, security_logger.info)
    log_fn(msg)

    # Also store in MongoDB for audit trail
    try:
        db = current_app.config.get('MONGO_DB')
        if db is not None:
            db['security_logs'].insert_one({
                'event_type': event_type,
                'ip_address': ip,
                'user_id': user_id,
                'user_agent': user_agent[:200],
                'details': str(details)[:1000],
                'timestamp': datetime.now(timezone.utc)
            })
    except Exception:
        # Don't let logging failures crash the app
        pass


# ─── Account Lockout ─────────────────────────────────────────────────────────

def check_account_lockout(email):
    """Check if an account is locked due to too many failed login attempts.

    Returns (is_locked, minutes_remaining).
    """
    try:
        db = current_app.config.get('MONGO_DB')
        if db is None:
            return False, 0

        max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
        lockout_minutes = current_app.config.get('LOGIN_LOCKOUT_MINUTES', 15)

        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=lockout_minutes)

        failed_count = db['security_logs'].count_documents({
            'event_type': 'LOGIN_FAILED',
            'details': {'$regex': re.escape(email)},
            'timestamp': {'$gte': cutoff}
        })

        if failed_count >= max_attempts:
            # Find the most recent failure to calculate remaining lockout
            latest = db['security_logs'].find_one(
                {
                    'event_type': 'LOGIN_FAILED',
                    'details': {'$regex': re.escape(email)},
                    'timestamp': {'$gte': cutoff}
                },
                sort=[('timestamp', -1)]
            )
            if latest:
                unlock_at = latest['timestamp'] + timedelta(minutes=lockout_minutes)
                remaining = (unlock_at - datetime.now(timezone.utc)).total_seconds() / 60
                return True, max(0, round(remaining))

        return False, 0
    except Exception:
        return False, 0
