"""
Mobile Banking API - Session Security Layer
Handles TLS session establishment for the customer-facing mobile app.
Migrated last year to hybrid key exchange as part of an early PQC pilot.
"""

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os

# Hybrid key exchange: classical X25519 combined with a post-quantum KEM
# (ML-KEM-768 handled by the hybrid_pqc_kem module, integrated via the
# bank's TLS 1.3 hybrid ciphersuite pilot - see ADR-2025-11).


def generate_classical_share():
    private_key = x25519.X25519PrivateKey.generate()
    return private_key


def derive_hybrid_session_key(x25519_shared: bytes, pqc_shared: bytes) -> bytes:
    """Combines classical ECDH output with PQC KEM output into one session key."""
    combined = x25519_shared + pqc_shared
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"hybrid-session").derive(combined)


def encrypt_session_payload(payload: bytes, key: bytes) -> bytes:
    cipher = ChaCha20Poly1305(key)
    nonce = os.urandom(12)
    return nonce + cipher.encrypt(nonce, payload, None)