"""
Certificate Reader - Phase 2, Step 4
Opens .crt certificate files and extracts real details: algorithm type,
key size, and expiry date.
"""

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from datetime import datetime, timezone


def read_certificate(filepath: str) -> dict:
    """Reads a .crt file and returns key details about it."""
    with open(filepath, "rb") as f:
        cert_bytes = f.read()

    cert = x509.load_pem_x509_certificate(cert_bytes)

    public_key = cert.public_key()

    # Figure out algorithm type and key size
    if isinstance(public_key, rsa.RSAPublicKey):
        algorithm = "RSA"
        key_size = public_key.key_size
    elif isinstance(public_key, ec.EllipticCurvePublicKey):
        algorithm = "ECC"
        key_size = public_key.curve.key_size
    else:
        algorithm = "Unknown"
        key_size = None

    expiry_date = cert.not_valid_after_utc
    days_until_expiry = (expiry_date - datetime.now(timezone.utc)).days

    return {
        "subject": cert.subject.rfc4514_string(),
        "algorithm": algorithm,
        "key_size": key_size,
        "expiry_date": expiry_date.strftime("%Y-%m-%d"),
        "days_until_expiry": days_until_expiry,
        "is_quantum_vulnerable": algorithm in ("RSA", "ECC"),
    }