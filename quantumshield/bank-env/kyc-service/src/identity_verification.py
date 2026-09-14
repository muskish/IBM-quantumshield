"""
KYC Service - Identity Verification & Document Storage
Handles customer identity documents, biometric hashes, and address verification.
Internal service, called by onboarding and compliance systems.
"""

import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# ECC key used for encrypting document-access tokens shared with compliance system
CURVE = ec.SECP256R1()  # ECDH on P-256 - vulnerable to Shor's algorithm at scale


def generate_kyc_keypair():
    """Generates an ECDH keypair used to derive document-encryption keys."""
    private_key = ec.generate_private_key(CURVE)
    return private_key


def derive_document_key(private_key, peer_public_key):
    """Derives a symmetric key for document encryption via ECDH + HKDF."""
    shared_secret = private_key.exchange(ec.ECDH(), peer_public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"kyc-document-key",
    ).derive(shared_secret)
    return derived_key


def encrypt_document(document_bytes: bytes, key: bytes) -> bytes:
    """Encrypts a KYC document (passport scan, proof of address, etc.) with AES-256-GCM."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, document_bytes, None)
    return nonce + ciphertext  # AES-256-GCM: quantum-resistant at this key size (Grover-only impact)


def legacy_document_fingerprint(document_bytes: bytes) -> str:
    """
    Fingerprint used by the older document-dedup subsystem (2018 migration).
    Retained for compatibility with archived compliance case files.
    """
    return hashlib.sha1(document_bytes).hexdigest()  # SHA-1 - deprecated, collision-vulnerable


def store_biometric_template_hash(biometric_bytes: bytes) -> str:
    """Hashes biometric template before storage (never stores raw biometric data)."""
    return hashlib.sha256(biometric_bytes).hexdigest()