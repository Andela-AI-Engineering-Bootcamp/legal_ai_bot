"""
Tool: find_similar_cases
=========================
Finds past court cases relevant to the user's situation.

In production this would use embeddings + vector search (Kelvin's section)
to find semantically similar cases across languages and countries.
For the demo we use a curated sample database.

Presentation example:
    User:  "I was fired without warning. What can I expect?"
    Agent: calls find_similar_cases(description="fired without warning", country="Nigeria")
    Tool returns similar precedents → agent tells user likely outcomes.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Sample case database (replace with vector DB lookup in production)
# ---------------------------------------------------------------------------

CASE_DATABASE: list[dict] = [
    # --- Nigeria ---
    {
        "case_name": "Adamu v. Sterling Industries Ltd (2020)",
        "country": "Nigeria",
        "court": "National Industrial Court",
        "topic": "wrongful dismissal",
        "summary": "Worker dismissed without prior warning or documented cause. Court ruled termination unfair.",
        "outcome": "Worker awarded 12 months salary as compensation plus ₦500,000 general damages.",
        "keywords": ["fired", "dismissed", "termination", "no warning", "unfair"],
    },
    {
        "case_name": "Okafor v. ElectroMart (2018)",
        "country": "Nigeria",
        "court": "Lagos State High Court",
        "topic": "defective goods",
        "summary": "Buyer purchased a phone that stopped working after 1 week. Seller refused refund.",
        "outcome": "Seller ordered to refund full purchase price plus ₦50,000 damages. Phone deemed unfit for purpose.",
        "keywords": ["refund", "defective", "phone", "product", "consumer"],
    },
    {
        "case_name": "Bello v. Skyline Properties (2019)",
        "country": "Nigeria",
        "court": "Lagos State Housing Court",
        "topic": "illegal eviction",
        "summary": "Landlord changed locks while tenant was at work without a court order.",
        "outcome": "Landlord ordered to restore access, pay ₦200,000 damages for unlawful eviction.",
        "keywords": ["eviction", "landlord", "locked out", "tenant", "rent"],
    },
    {
        "case_name": "Musa v. Al-Bashir Enterprises (2021)",
        "country": "Nigeria",
        "court": "National Industrial Court",
        "topic": "unpaid wages",
        "summary": "Employer withheld 3 months salary claiming 'cash flow issues'.",
        "outcome": "Employer ordered to pay all outstanding wages plus 10% interest per month of delay.",
        "keywords": ["salary", "unpaid", "wages", "deduction", "owed"],
    },
    # --- Ghana ---
    {
        "case_name": "Mensah v. Goldfields Corp (2021)",
        "country": "Ghana",
        "court": "Court of Appeal, Accra",
        "topic": "unfair termination",
        "summary": "Employee dismissed after reporting safety violations. Court found dismissal retaliatory.",
        "outcome": "Employee awarded 6 months salary plus reinstatement to former position.",
        "keywords": ["fired", "dismissed", "whistleblower", "retaliation", "termination"],
    },
    {
        "case_name": "Owusu v. Accra Housing Ltd (2022)",
        "country": "Ghana",
        "court": "Rent Tribunal, Accra",
        "topic": "rent increase",
        "summary": "Landlord increased rent by 40% without proper notice. Tenant challenged at tribunal.",
        "outcome": "Increase reduced to 25% (statutory max). Landlord warned for non-compliance.",
        "keywords": ["rent", "increase", "landlord", "tenant", "eviction"],
    },
    # --- Kenya ---
    {
        "case_name": "Wanjiku v. TechStart Ltd (2022)",
        "country": "Kenya",
        "court": "Employment and Labour Relations Court",
        "topic": "wrongful dismissal",
        "summary": "Software developer terminated without valid reason after 2 years of employment.",
        "outcome": "Worker awarded 12 months salary as compensation. Employer to issue certificate of service.",
        "keywords": ["fired", "dismissed", "termination", "no reason", "unfair"],
    },
    {
        "case_name": "Kamau v. MegaSupply Ltd (2020)",
        "country": "Kenya",
        "court": "High Court, Nairobi",
        "topic": "unfair contract",
        "summary": "Trader signed supply contract with one-sided liability clause. Court found it unconscionable.",
        "outcome": "Unfair clause voided under Law of Contract Act, Cap 23 Section 14. Contract renegotiated.",
        "keywords": ["contract", "unfair", "liability", "supplier", "unconscionable"],
    },
]


def find_similar_cases(
    description: str,
    country: str = "",
    topic: str = "",
    max_results: int = 3,
) -> dict:
    """Find past court cases similar to the user's legal situation.

    Use this tool when the user describes a dispute and wants to know
    what happened in similar cases, likely outcomes, or precedents.

    Args:
        description: Plain-language description of the user's situation.
        country:     Optional — filter to a specific country.
        topic:       Optional — filter by topic (e.g. "wrongful dismissal").
        max_results: Maximum number of cases to return (default 3).

    Returns:
        A dict with matching cases, including outcomes and court details.
    """
    if not description or not description.strip():
        return {"error": "Please describe your legal situation so I can find similar cases."}

    desc_lower = description.lower()
    query_words = set(desc_lower.split())

    scored_cases: list[tuple[int, dict]] = []

    for case in CASE_DATABASE:
        # Filter by country if specified
        if country and case["country"].lower() != country.lower():
            continue
        # Filter by topic if specified
        if topic and topic.lower() not in case["topic"].lower():
            continue

        # Score by keyword overlap with description
        score = 0
        for kw in case["keywords"]:
            if kw in desc_lower:
                score += 2  # exact keyword match
            elif any(kw in word or word in kw for word in query_words):
                score += 1  # partial match

        # Also check summary
        for word in query_words:
            if len(word) > 3 and word in case["summary"].lower():
                score += 1

        if score > 0:
            scored_cases.append((score, case))

    # Sort by relevance score (highest first)
    scored_cases.sort(key=lambda x: x[0], reverse=True)
    top_cases = [case for _, case in scored_cases[:max_results]]

    if not top_cases:
        return {
            "found": False,
            "message": "No similar cases found. Try broadening your description or removing country/topic filters.",
        }

    return {
        "found": True,
        "query": description,
        "cases": [
            {
                "case_name": c["case_name"],
                "country": c["country"],
                "court": c["court"],
                "topic": c["topic"],
                "summary": c["summary"],
                "outcome": c["outcome"],
            }
            for c in top_cases
        ],
        "count": len(top_cases),
        "note": "These are illustrative precedents. Actual outcomes depend on case specifics.",
    }
