from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import secrets
import string

ALPHABET = string.ascii_letters + string.digits

def generate_code128(length: int = 12) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

def generate_barcode_image(code: str) -> BytesIO:
    barcode_obj = barcode.get(
        "code128",
        code,
        writer=ImageWriter()
    )

    buffer = BytesIO()
    barcode_obj.write(buffer)
    buffer.seek(0)

    return buffer