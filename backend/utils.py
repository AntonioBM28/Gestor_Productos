import qrcode
import io
import base64
import uuid
import random
import string


def generate_reference_code():
    """Generate a unique reference code for Oxxo-style payments."""
    prefix = 'GPC'
    timestamp_part = uuid.uuid4().hex[:8].upper()
    random_part = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}-{timestamp_part}-{random_part}"


def generate_qr_base64(data: str) -> str:
    """Generate a QR code as a base64-encoded PNG string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def generate_barcode_number():
    """Generate a 16-digit barcode number for payment reference."""
    return ''.join(random.choices(string.digits, k=16))
