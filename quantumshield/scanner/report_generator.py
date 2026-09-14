"""
Report Generator - Phase 2, Step 5
Combines source code findings and certificate findings into one
structured CBOM (Cryptography Bill of Materials) file.
"""

import json
from datetime import datetime, timezone


def build_cbom(source_findings: dict, certificate_findings: dict) -> dict:
    """
    Combines findings into one structured CBOM document.
    source_findings and certificate_findings are dicts keyed by service name.
    """
    cbom = {
        "report_generated_at": datetime.now(timezone.utc).isoformat(),
        "report_type": "Cryptography Bill of Materials (CBOM)",
        "services": {},
    }

    all_service_names = set(source_findings.keys()) | set(certificate_findings.keys())

    for service_name in sorted(all_service_names):
        cbom["services"][service_name] = {
            "source_code_findings": source_findings.get(service_name, []),
            "certificate_findings": certificate_findings.get(service_name, []),
        }

    return cbom


def save_cbom(cbom: dict, output_path: str):
    """Writes the CBOM dictionary to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cbom, f, indent=2)
    print(f"\nCBOM report saved to: {output_path}")