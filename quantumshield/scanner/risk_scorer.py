"""
Risk Scoring Engine - Phase 5
Combines crypto findings with business context into one explainable
risk score per service, using a weighted scoring model.
"""

# How much each crypto risk category contributes to the score
ALGORITHM_RISK_WEIGHTS = {
    "quantum_vulnerable": 3,
    "weak_classical": 2,
    "strong": 0,
    "quantum_safe": -1,  # actually reduces risk - rewards good practice
}

# How much each data sensitivity level multiplies the score
SENSITIVITY_MULTIPLIERS = {
    "critical": 3.0,
    "high": 2.0,
    "medium": 1.5,
    "none": 0.2,
    "unknown": 1.0,
}


def score_crypto_findings(source_findings: list, certificate_findings: list) -> tuple:
    """Returns (raw_score, list of explanation strings) from algorithm findings."""
    raw_score = 0
    explanations = []

    for finding in source_findings:
        weight = ALGORITHM_RISK_WEIGHTS.get(finding["risk_category"], 0)
        contribution = weight * min(finding["occurrences"], 5)  # cap so one algo can't dominate
        raw_score += contribution
        if weight > 0:
            explanations.append(
                f"{finding['algorithm']} found {finding['occurrences']}x "
                f"({finding['risk_category']}, contributes +{contribution})"
            )
        elif weight < 0:
            explanations.append(
                f"{finding['algorithm']} found - already quantum-safe (contributes {contribution})"
            )

    for cert in certificate_findings:
        if cert.get("is_quantum_vulnerable"):
            raw_score += 3
            explanations.append(
                f"Certificate uses {cert['algorithm']} ({cert['key_size']} bits) - quantum-vulnerable (+3)"
            )

    return raw_score, explanations


def calculate_risk_score(service_name: str, source_findings: list,
                          certificate_findings: list, business_context: dict) -> dict:
    """Calculates a final, explainable risk score for one service."""

    raw_crypto_score, crypto_explanations = score_crypto_findings(source_findings, certificate_findings)

    sensitivity = business_context.get("data_sensitivity", "unknown")
    sensitivity_multiplier = SENSITIVITY_MULTIPLIERS.get(sensitivity, 1.0)

    exposure_bonus = 2.0 if business_context.get("public_exposure") else 0.0

    retention_years = business_context.get("retention_period_years", 0)
    retention_bonus = min(retention_years / 5.0, 3.0)  # caps out at +3 for very long retention

    agility_bonus = 0.0 if business_context.get("algorithm_configurable_at_runtime") else 1.0

    final_score = (raw_crypto_score * sensitivity_multiplier) + exposure_bonus + retention_bonus + agility_bonus
    final_score = round(max(final_score, 0), 1)

    # Convert numeric score into a plain-language risk level
    if final_score >= 80:
        risk_level = "Critical"
    elif final_score >= 20:
        risk_level = "High"
    elif final_score >= 5:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    explanation_summary = list(crypto_explanations)
    explanation_summary.append(
        f"Data sensitivity '{sensitivity}' applies a x{sensitivity_multiplier} multiplier"
    )
    if exposure_bonus:
        explanation_summary.append(f"Public-facing service adds +{exposure_bonus}")
    if retention_bonus:
        explanation_summary.append(
            f"{retention_years}-year data retention adds +{round(retention_bonus, 1)}"
        )
    if agility_bonus:
        explanation_summary.append("Cryptography is hardcoded/not runtime-configurable, adds +1")

    return {
        "service_name": service_name,
        "risk_score": final_score,
        "risk_level": risk_level,
        "explanation": explanation_summary,
    }