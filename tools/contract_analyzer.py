"""
Tool: analyze_contract
=======================
Extracts key terms from contract text and flags risky / non-standard clauses.

Presentation example:
    User:  "I'm buying ₦2M of fabric. Supplier sent me this contract."
    Agent: calls analyze_contract(contract_text="...", country="Nigeria")
    Tool returns flagged clauses → agent warns the user before they sign.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Risky-clause patterns (keyword-based for demo; swap for NLP in production)
# ---------------------------------------------------------------------------

RISKY_PATTERNS: list[dict] = [
    {
        "pattern": "buyer liable for all",
        "risk": "HIGH",
        "reason": "Shifts ALL liability to buyer — non-standard. Supplier should bear own losses unless buyer explicitly causes them.",
        "suggestion": "Replace with: 'Each party shall be liable only for losses directly caused by its own breach.'",
    },
    {
        "pattern": "no refund",
        "risk": "HIGH",
        "reason": "Eliminates refund rights even for defective goods — may violate consumer protection law.",
        "suggestion": "Add: 'Buyer is entitled to a full refund if goods are defective or not as described.'",
    },
    {
        "pattern": "non-compete",
        "risk": "MEDIUM",
        "reason": "Non-compete clauses can restrict future livelihood. Often unenforceable in African jurisdictions.",
        "suggestion": "Limit scope: restrict to specific industry, geography, and max 6-12 months.",
    },
    {
        "pattern": "automatic renewal",
        "risk": "MEDIUM",
        "reason": "Contract renews without explicit consent — could trap party in unwanted obligations.",
        "suggestion": "Change to: 'Renewal requires written agreement from both parties at least 30 days before expiry.'",
    },
    {
        "pattern": "penalty",
        "risk": "MEDIUM",
        "reason": "Penalty clauses may be unenforceable if disproportionate to actual loss.",
        "suggestion": "Replace 'penalty' with 'liquidated damages' and tie amount to estimated actual loss.",
    },
    {
        "pattern": "waive all rights",
        "risk": "HIGH",
        "reason": "Blanket waiver of rights is typically unconscionable and may be void.",
        "suggestion": "Remove clause entirely or limit waiver to specific, clearly defined rights.",
    },
    {
        "pattern": "sole discretion",
        "risk": "MEDIUM",
        "reason": "Gives one party unchecked power to make decisions affecting both parties.",
        "suggestion": "Add: 'Such discretion shall be exercised reasonably and in good faith.'",
    },
    {
        "pattern": "indemnify",
        "risk": "LOW",
        "reason": "Indemnification is standard but should be mutual — check if only one party indemnifies.",
        "suggestion": "Ensure indemnification is mutual or limited to each party's own negligence.",
    },
]

# Standard contract sections that should be present
EXPECTED_SECTIONS = [
    "payment terms",
    "delivery",
    "cancellation",
    "dispute resolution",
    "liability",
    "governing law",
]


def analyze_contract(contract_text: str, country: str = "Nigeria") -> dict:
    """Analyze contract text for risky or non-standard clauses.

    Use this tool when a user shares contract text and wants to know
    if it is fair, what risks exist, or what to negotiate before signing.

    Args:
        contract_text: The full text of the contract to analyze.
        country:       Country whose law applies (for context in suggestions).

    Returns:
        A dict with flagged clauses, missing sections, and an overall risk score.
    """
    if not contract_text or not contract_text.strip():
        return {"error": "No contract text provided. Please paste the contract text."}

    text_lower = contract_text.lower()

    # --- Flag risky clauses ---
    flagged_clauses = []
    for pattern in RISKY_PATTERNS:
        if pattern["pattern"] in text_lower:
            flagged_clauses.append({
                "clause_trigger": pattern["pattern"],
                "risk_level": pattern["risk"],
                "reason": pattern["reason"],
                "suggestion": pattern["suggestion"],
            })

    # --- Check for missing standard sections ---
    missing_sections = [
        section for section in EXPECTED_SECTIONS
        if section not in text_lower
    ]

    # --- Overall risk assessment ---
    high_count = sum(1 for c in flagged_clauses if c["risk_level"] == "HIGH")
    medium_count = sum(1 for c in flagged_clauses if c["risk_level"] == "MEDIUM")

    if high_count >= 2:
        overall_risk = "HIGH — Do NOT sign without legal review"
    elif high_count == 1 or medium_count >= 2:
        overall_risk = "MEDIUM — Negotiate flagged clauses before signing"
    elif flagged_clauses:
        overall_risk = "LOW — Minor issues, generally acceptable"
    else:
        overall_risk = "LOW — No obvious risky clauses detected"

    return {
        "country": country,
        "overall_risk": overall_risk,
        "flagged_clauses": flagged_clauses,
        "flagged_count": len(flagged_clauses),
        "missing_sections": missing_sections,
        "missing_count": len(missing_sections),
        "recommendation": (
            f"Review this contract under {country} law. "
            f"{len(flagged_clauses)} clause(s) flagged, "
            f"{len(missing_sections)} standard section(s) missing."
        ),
    }
