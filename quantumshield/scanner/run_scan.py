"""
Run Scan - Phase 2 + Phase 4 + Phase 5
Scans the fake bank environment, attaches business context, calculates
explainable risk scores, and saves a combined CBOM + risk report.
"""

from file_walker import find_relevant_files, BANK_ENV_PATH
from crypto_detector import scan_file_for_crypto
from cert_reader import read_certificate
from config_reader import read_service_config
from report_generator import build_cbom, save_cbom
from risk_scorer import calculate_risk_score
from roadmap_generator import build_migration_roadmap

def get_service_name(filepath: str) -> str:
    normalized = filepath.replace("\\", "/")
    parts = normalized.split("/")
    for part in parts:
        if part not in (".", "..", "bank-env"):
            return part
    return "unknown"


def scan_source_code(all_files) -> dict:
    source_files = [f for f, ftype in all_files if ftype == "source code"]
    results = {}
    for filepath in source_files:
        service_name = get_service_name(filepath)
        results[service_name] = scan_file_for_crypto(filepath)
    return results


def scan_certificates(all_files) -> dict:
    cert_files = [f for f, ftype in all_files if ftype == "certificate"]
    results = {}
    for filepath in cert_files:
        service_name = get_service_name(filepath)
        try:
            details = read_certificate(filepath)
            results.setdefault(service_name, []).append(details)
        except Exception as e:
            print(f"  Could not read certificate {filepath}: {e}")
    return results


def scan_service_configs(all_files) -> dict:
    config_files = [f for f, ftype in all_files if ftype == "service config/blueprint"]
    results = {}
    for filepath in config_files:
        service_name = get_service_name(filepath)
        try:
            results[service_name] = read_service_config(filepath)
        except Exception as e:
            print(f"  Could not read config {filepath}: {e}")
    return results


def main():
    print(f"Scanning folder: {BANK_ENV_PATH}\n")
    all_files = find_relevant_files(BANK_ENV_PATH)

    source_findings = scan_source_code(all_files)
    certificate_findings = scan_certificates(all_files)
    business_context = scan_service_configs(all_files)

    cbom = build_cbom(source_findings, certificate_findings)

    print("========== RISK SCORES ==========\n")

    risk_results = []
    for service_name in sorted(business_context.keys()):
        context = business_context[service_name]
        src_findings = source_findings.get(service_name, [])
        cert_findings = certificate_findings.get(service_name, [])

        risk = calculate_risk_score(service_name, src_findings, cert_findings, context)
        risk_results.append(risk)

        print(f"=== {service_name} ===")
        print(f"  Risk Score: {risk['risk_score']}  |  Risk Level: {risk['risk_level']}")
        for line in risk['explanation']:
            print(f"    - {line}")
        print()

        # Attach to CBOM
        if service_name in cbom["services"]:
            cbom["services"][service_name]["business_context"] = context
            cbom["services"][service_name]["risk_assessment"] = risk

    # Sort and print a priority ranking
    risk_results.sort(key=lambda r: r["risk_score"], reverse=True)
    print("========== PRIORITY RANKING (highest risk first) ==========\n")
    for i, risk in enumerate(risk_results, start=1):
        print(f"{i}. {risk['service_name']} - {risk['risk_level']} ({risk['risk_score']})")

        roadmap = build_migration_roadmap(cbom["services"])
    cbom["migration_roadmap"] = roadmap

    print("========== MIGRATION ROADMAP ==========\n")
    phase_labels = {1: "Phase 1 - Critical (fix immediately)",
                     2: "Phase 2 - High (fix soon)",
                     3: "Phase 3 - Medium (plan for)",
                     4: "Phase 4 - Low (monitor)"}
    for phase_num in sorted(roadmap.keys()):
        print(f"--- {phase_labels[phase_num]} ---")
        if not roadmap[phase_num]:
            print("  (no services in this phase)")
        for item in roadmap[phase_num]:
            print(f"  {item['service_name']} ({item['risk_level']}, score {item['risk_score']})")
            for action in item["actions"]:
                print(f"    -> {action}")
        print()

    save_cbom(cbom, "cbom_report.json")


if __name__ == "__main__":
    main()