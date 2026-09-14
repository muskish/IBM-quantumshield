"""
Config Reader - Phase 4, Step 1
Reads each service's service.yaml blueprint and extracts the business
context needed for risk scoring: exposure, data sensitivity, retention,
vendor dependency, and crypto-agility.
"""

import yaml


def read_service_config(filepath: str) -> dict:
    """Reads a service.yaml file and returns its key business-context fields."""
    with open(filepath, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    network = config.get("network", {})
    data_classification = config.get("data_classification", {})
    crypto_agility = config.get("crypto_agility", {})
    vendor_dependencies = config.get("vendor_dependencies", [])

    return {
        "service_name": config.get("service_name", "unknown"),
        "description": config.get("description", "").strip(),
        "public_exposure": network.get("public_exposure", False),
        "internet_facing": network.get("internet_facing", False),
        "tls_min_version": network.get("tls_min_version", "unknown"),
        "data_sensitivity": data_classification.get("sensitivity", "unknown"),
        "data_types": data_classification.get("primary_data_types", []),
        "retention_period_years": data_classification.get("retention_period_years", 0),
        "vendor_dependencies": vendor_dependencies,
        "algorithm_configurable_at_runtime": crypto_agility.get("algorithm_configurable_at_runtime", False),
        "business_criticality": config.get("business_criticality", "unknown"),
    }