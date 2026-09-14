"""
Loan Service - Document Storage & Inter-Branch Sync
Stores signed loan agreements, amortization schedules, and collateral records.
Syncs encrypted document bundles between branch offices nightly.
"""

from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.fernet import Fernet
import hashlib

# Diffie-Hellman parameters used for branch-to-branch key agreement
# Generated once in 2015, reused across all branch sync sessions since.
DH_PARAMETERS_BITS = 1024  # Weak - well below recommended 2048+ minimum


def load_dh_parameters():
    """Loads the shared DH parameter set for branch synchronization."""
    parameters = dh.generate_parameters(generator=2, key_size=DH_PARAMETERS_BITS)
    return parameters


def generate_branch_keypair(parameters):
    private_key = parameters.generate_private_key()
    return private_key


def derive_sync_key(private_key, peer_public_key):
    shared_key = private_key.exchange(peer_public_key)
    derived = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"branch-sync").derive(shared_key)
    return derived


def encrypt_loan_bundle(bundle_bytes: bytes, fernet_key: bytes) -> bytes:
    """Encrypts loan document bundle for inter-branch transfer (AES-128-CBC + HMAC under Fernet)."""
    f = Fernet(fernet_key)
    return f.encrypt(bundle_bytes)


def loan_agreement_checksum(agreement_bytes: bytes) -> str:
    """Checksum stored alongside archived loan agreements for integrity checks."""
    return hashlib.sha256(agreement_bytes).hexdigest()


def signature_key_reference() -> dict:
    """Loan agreements are digitally signed using the bank's central RSA-2048 signing authority."""
    return {
        "signing_authority": "central-signing-service",
        "algorithm": "RSA-2048",
        "certificate_ref": "certs/loan_signing_rsa2048.crt",
    }