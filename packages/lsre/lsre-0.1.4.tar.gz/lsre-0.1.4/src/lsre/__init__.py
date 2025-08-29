"""Root `lsre` class."""

import sys

from loguru import logger

from .regex_functions import (
    is_alphanumeric,
    is_credit_card,
    is_email,
    is_hex_color,
    is_ipv4,
    is_ipv6,
    is_iso_date,
    is_phone_number,
    is_slug,
    is_strong_password,
    is_time,
    is_url,
    is_uuid,
)

logger.remove()  # Remove default handler
logger.add(sys.stderr, level='INFO')

__all__ = [
    'is_alphanumeric',
    'is_credit_card',
    'is_email',
    'is_hex_color',
    'is_ipv4',
    'is_ipv6',
    'is_iso_date',
    'is_phone_number',
    'is_slug',
    'is_strong_password',
    'is_time',
    'is_url',
    'is_uuid',
]
