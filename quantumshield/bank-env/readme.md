# QuantumShield Banking — Synthetic Demo Environment

This is a **fictional, self-contained** multi-service banking environment
built purely to demonstrate the QuantumShield Banking scanner. No real bank,
customer, or vendor is represented. All certificates and keys are generated
locally for this demo and are not used anywhere else.

## Services

| Service | Public? | Data Sensitivity | Retention | Crypto Highlights | Expected Risk |
|---|---|---|---|---|---|
| `payment-gateway` | Yes | Critical (PCI) | 12 yrs | RSA-2048 signing, MD5 legacy hash, 3DES batch encryption, TLS 1.0 allowed | **Critical** |
| `kyc-service` | No | Critical (PII) | 10 yrs | ECDH P-256, SHA-1 legacy fingerprint, AES-256-GCM documents | **High** |
| `loan-service` | No | High (financial) | 15 yrs | DH-1024 (weak params), RSA-2048 signing authority, Fernet storage | **High** |
| `internal-test-app` | No | None (synthetic only) | 0 yrs | DES-ECB, MD5 — weak, but zero real data exposure | **Low** |
| `mobile-banking-api` | Yes | High (sessions) | 2 yrs | Hybrid X25519 + ML-KEM-768, ChaCha20-Poly1305 | **Low/Informational** |

## Why it's built this way

The scanner (Phase 2 onward) needs a mix of:
- **Obviously vulnerable** crypto tied to **high-sensitivity, long-retention, public-facing** data → should surface as top priority (`payment-gateway`).
- **Vulnerable-but-lower-exposure** crypto → should still rank high, but not #1 (`kyc-service`, `loan-service`).
- **Weak crypto with no real data behind it** → should score low, proving the engine reasons about *impact*, not just *algorithm strength* (`internal-test-app`).
- **A service already doing the right thing** → proves the tool doesn't just flag everything red, and gives a positive example to show judges (`mobile-banking-api`).

Each service folder contains:
- `src/` — source code with real crypto library calls (some weak, some strong)
- `config/service.yaml` — data classification, exposure, vendor, and crypto-agility metadata (stands in for the kind of context a real CMDB/data-catalog would supply)
- `requirements.txt` — dependency versions, some intentionally outdated
- `certs/` — real self-signed certificates for services with public-facing endpoints