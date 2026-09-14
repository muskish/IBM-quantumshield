"""
Internal Test App - QA / Staging Harness
Used by QA engineers to generate synthetic transactions and test payloads.
Never touches real customer data. Deployed only in internal staging network.
"""

import hashlib
from Crypto.Cipher import DES

# Toy encryption used purely to obfuscate synthetic test fixtures in logs.
# No real customer or financial data ever passes through this app.


def obfuscate_test_payload(payload: bytes, key: bytes) -> bytes:
    cipher = DES.new(key, DES.MODE_ECB)  # DES - broken, but only ever applied to synthetic test data
    return cipher.encrypt(payload)


def fixture_checksum(fixture_bytes: bytes) -> str:
    return hashlib.md5(fixture_bytes).hexdigest()  # MD5 - weak, but zero real-world sensitivity here


def generate_synthetic_card_number() -> str:
    """Generates a fake, non-real card number pattern for test fixtures (Luhn-valid but fictional BIN)."""
    return "4000-0000-0000-0002"