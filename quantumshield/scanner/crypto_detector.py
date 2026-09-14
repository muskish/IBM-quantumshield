"""
Crypto Pattern Detector - Phase 2, Step 2
Scans the text of source code files for known cryptographic algorithm
usage, and classifies each finding as weak/quantum-vulnerable or strong.
"""

import re

# Each entry: (pattern to search for, human-readable algorithm name, risk category)
# risk category options: "weak_classical", "quantum_vulnerable", "strong"
CRYPTO_PATTERNS = [
    (r"\bMD5\b|hashlib\.md5", "MD5", "weak_classical"),
    (r"\bSHA1\b|hashlib\.sha1", "SHA-1", "weak_classical"),
    (r"\bDES3\b|Crypto\.Cipher\.DES3|DES3\.new", "3DES", "weak_classical"),
    (r"(?<!3)\bDES\b|Crypto\.Cipher\.DES(?!3)", "DES", "weak_classical"),
    (r"\bRSA\b|Crypto\.PublicKey\.RSA|rsa\.generate", "RSA", "quantum_vulnerable"),
    (r"\bdh\.generate_parameters\b|Diffie.?Hellman|\bDH\b", "Diffie-Hellman", "quantum_vulnerable"),
    (r"\bec\.SECP256R1\b|\bECDH\b|elliptic.?curve", "ECC/ECDH", "quantum_vulnerable"),
    (r"\bAES256\b|AES.256|AESGCM", "AES-256", "strong"),
    (r"\bAES128\b|AES.128|Fernet", "AES-128 (Fernet)", "strong"),
    (r"\bSHA256\b|hashlib\.sha256|SHA256\(\)", "SHA-256", "strong"),
    (r"\bChaCha20Poly1305\b", "ChaCha20-Poly1305", "strong"),
    (r"\bx25519\b|X25519PrivateKey", "X25519", "strong"),
    (r"ML.?KEM|post.?quantum|hybrid.?pqc", "Hybrid PQC (ML-KEM)", "quantum_safe"),
    (r"TLSv1_0|TLSv1\.0|PROTOCOL_TLS.*1_0", "TLS 1.0 (outdated protocol)", "weak_classical"),
]


def scan_file_for_crypto(filepath: str) -> list:
    """Reads a source file's text and returns all crypto patterns found in it."""
    findings = []

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    for pattern, algorithm_name, risk_category in CRYPTO_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            findings.append({
                "algorithm": algorithm_name,
                "risk_category": risk_category,
                "occurrences": len(matches),
            })

    return findings