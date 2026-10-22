"""QR code rendering."""

from io import BytesIO

import qrcode
from aiogram.types import BufferedInputFile


def make_qr_file(value: str, filename: str = "payment-qr.png") -> BufferedInputFile:
    """Create Telegram input file with QR code."""

    image = qrcode.make(value)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return BufferedInputFile(buffer.getvalue(), filename=filename)
