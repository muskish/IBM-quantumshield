"""
Migration Roadmap Generator - Phase 8
Turns risk-ranked findings into a phased, actionable migration plan
with concrete remediation steps per service.
"""

# Maps each algorithm to a concrete, specific recommended action
REMEDIATION_ACTIONS = {
    "RSA": "Plan migration to a post-quantum or hybrid signature scheme (e.g. ML-DSA or hybrid RSA+ML-DSA).",
    "Diffie-Hellman": "Replace classical DH key exchange with a hybrid classical+PQC KEM (e.g. X25519+ML-KEM).",
    "ECC/ECDH": "Migrate to a hybrid key exchange combining ECDH with a post-quantum KEM (e.g. ML-KEM-768).",
    "MD5": "Replace MD5 with SHA-256 or SHA-3 for any integrity/hashing use case.",
    "SHA-1": "Replace SHA-1 with SHA-256 for all hashing and fingerprinting.",
    "3DES": "Replace 3DES with AES-256-GCM for data-at-rest and in-transit encryption.",
    "DES": "Replace DES with AES-256-GCM immediately; DES is broken by modern standards.",
    "TLS 1.0 (outdated protocol)": "Disable TLS 1.0/1.1 support; enforce TLS 1.3 with modern cipher suites.",
}

GENERIC_VENDOR_ACTION = "Confirm vendor's post-quantum migration roadmap and require hybrid cryptography support contractually."
GENERIC_CERT_ACTION = "Reissue certificate using a hybrid or post-quantum-ready algorithm ahead of expiry."


def build_remediation_list(service_data: dict) -> list:
    """Builds a de-duplicated list of concrete remediation actions for one service."""
    actions = []
    seen = set()

    for finding in service_data.get("source_code_findings", []):
        algo = finding["algorithm"]
        if finding["risk_category"] in ("weak_classical", "quantum_vulnerable") and algo in REMEDIATION_ACTIONS:
            action = REMEDIATION_ACTIONS[algo]
            if action not in seen:
                actions.append(action)
                seen.add(action)

    for cert in service_data.get("certificate_findings", []):
        if cert.get("is_quantum_vulnerable") and GENERIC_CERT_ACTION not in seen:
            actions.append(GENERIC_CERT_ACTION)
            seen.add(GENERIC_CERT_ACTION)

    context = service_data.get("business_context", {})
    vendors = context.get("vendor_dependencies", [])
    for vendor in vendors:
        if vendor.get("name") and vendor.get("name") != "none" and not vendor.get("quantum_safe_roadmap_confirmed"):
            if GENERIC_VENDOR_ACTION not in seen:
                actions.append(GENERIC_VENDOR_ACTION)
                seen.add(GENERIC_VENDOR_ACTION)

    return actions


def assign_phase(risk_level: str) -> int:
    """Maps a risk level to a migration phase number (1 = most urgent)."""
    mapping = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4,
    }
    return mapping.get(risk_level, 4)


def build_migration_roadmap(cbom_services: dict) -> dict:
    """
    Builds a full phased roadmap from the CBOM's services data.
    Returns a dict: { phase_number: [ {service_name, risk_level, risk_score, actions}, ... ] }
    """
    roadmap = {1: [], 2: [], 3: [], 4: []}

    for service_name, service_data in cbom_services.items():
        risk = service_data.get("risk_assessment", {})
        risk_level = risk.get("risk_level", "Low")
        phase = assign_phase(risk_level)

        actions = build_remediation_list(service_data)

        roadmap[phase].append({
            "service_name": service_name,
            "risk_level": risk_level,
            "risk_score": risk.get("risk_score", 0),
            "actions": actions,
        })

    # Sort services within each phase by risk score, highest first
    for phase_num in roadmap:
        roadmap[phase_num].sort(key=lambda s: s["risk_score"], reverse=True)

    return roadmap