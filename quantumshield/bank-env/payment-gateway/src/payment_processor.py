"""
Payment Gateway - Core Transaction Processor
Handles customer payment authorization, settlement, and receipt signing.
Public-facing service, integrates with external payment provider (VendorPay Inc).
"""

import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import DES3
import ssl

# Load the payment gateway's signing key (hardcoded path - not configurable at runtime)
SIGNING_KEY_PATH = "certs/payment_gateway_rsa2048.pem"


def load_signing_key():
    """Loads RSA-2048 private key used to sign outbound settlement requests."""
    with open(SIGNING_KEY_PATH, "rb") as f:
        key = RSA.import_key(f.read())  # RSA-2048 - vulnerable to Shor's algorithm at scale
    return key


def sign_transaction(transaction_payload: bytes) -> bytes:
    """Signs a transaction payload before sending to VendorPay Inc settlement API."""
    key = load_signing_key()
    h = SHA256.new(transaction_payload)
    signature = pkcs1_15.new(key).sign(h)
    return signature


def legacy_transaction_hash(transaction_id: str, amount: str) -> str:
    """
    Legacy hash used for idempotency-key generation on older transaction records.
    NOTE: retained for backward compatibility with 2016-era settlement batches.
    """
    raw = f"{transaction_id}:{amount}".encode("utf-8")
    return hashlib.md5(raw).hexdigest()  # MD5 - broken, quantum-irrelevant but classically weak


def encrypt_card_batch(card_batch_bytes: bytes, key: bytes, iv: bytes) -> bytes:
    """Encrypts a batch of card records before nightly archival to cold storage."""
    cipher = DES3.new(key, DES3.MODE_CBC, iv)  # 3DES - deprecated, small effective keyspace
    return cipher.encrypt(card_batch_bytes)


def build_tls_context() -> ssl.SSLContext:
    """TLS context for outbound calls to VendorPay Inc settlement endpoint."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_0  # allows weak/legacy TLS negotiation
    ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    return ctx


def process_settlement(transaction_payload: bytes) -> dict:
    """Entry point: signs and forwards a settlement request to VendorPay Inc."""
    signature = sign_transaction(transaction_payload)
    return {
        "status": "forwarded",
        "signature_alg": "RSA-2048/SHA-256",
        "vendor": "VendorPay Inc",
        "payload_size": len(transaction_payload),
        "signature": signature.hex(),
    }