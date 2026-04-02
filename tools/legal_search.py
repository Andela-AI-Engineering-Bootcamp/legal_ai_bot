"""
Tool: search_legal_database
============================
Looks up statutes, acts, and legal provisions for African countries.

This is the core reference tool — when a citizen asks "Is X legal?",
the agent calls this tool to retrieve the actual statute text so it can
ground its answer in real law (works hand-in-hand with the RAG module).

Presentation example:
    User:  "My boss deducted ₦10,000 from my salary for being late."
    Agent: calls search_legal_database(country="Nigeria", topic="salary deduction")
    Tool returns Section 12 of the Nigerian Labor Act → agent cites it.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Sample legal database (replace with a real DB / vector store in production)
# ---------------------------------------------------------------------------

LEGAL_DATABASE: dict[str, dict[str, list[dict]]] = {
    "Nigeria": {
        "labor": [
            {
                "statute": "Nigerian Labor Act, 2004",
                "section": "Section 12",
                "title": "Permissible Deductions from Wages",
                "text": (
                    "No employer shall make any deduction from the wages of a "
                    "worker except: (a) Taxes, (b) Contributions to provident "
                    "or pension funds, (c) Union dues, (d) Amounts owing to the "
                    "employer by the worker. Deductions for lateness, mistakes, "
                    "or poor performance are PROHIBITED."
                ),
                "penalty": "Worker may claim full refund plus damages at Ministry of Labor (FREE).",
            },
            {
                "statute": "Nigerian Labor Act, 2004",
                "section": "Section 11(1)",
                "title": "Payment of Wages",
                "text": (
                    "Wages shall be paid at intervals not exceeding one month "
                    "and in legal tender. Wages must not be paid in vouchers, "
                    "coupons, or any form other than legal tender."
                ),
                "penalty": "Employer liable for unpaid wages plus interest.",
            },
        ],
        "tenancy": [
            {
                "statute": "Lagos Tenancy Law, 2011",
                "section": "Section 13",
                "title": "Notice to Quit",
                "text": (
                    "A landlord must give a tenant written notice of at least "
                    "6 months before terminating a yearly tenancy. Locking out "
                    "a tenant without a valid court order is illegal."
                ),
                "penalty": "Tenant may sue for unlawful eviction at Lagos State Housing Court (₦500 filing fee).",
            },
        ],
        "consumer": [
            {
                "statute": "Federal Competition and Consumer Protection Act, 2019 (FCCPA)",
                "section": "Section 114",
                "title": "Right to Return Defective Goods",
                "text": (
                    "A consumer who purchases goods that are defective or not "
                    "fit for purpose is entitled to a repair, replacement, or "
                    "full refund within 30 days of purchase."
                ),
                "penalty": "File complaint at FCCPC (Federal Competition & Consumer Protection Commission) - FREE.",
            },
        ],
    },
    "Ghana": {
        "labor": [
            {
                "statute": "Ghana Labour Act, 2003 (Act 651)",
                "section": "Section 70",
                "title": "Unfair Termination",
                "text": (
                    "A termination of employment is unfair if no valid reason "
                    "is given relating to the worker's capacity, conduct, or "
                    "operational requirements. Employer must give written "
                    "reasons within 7 days of request."
                ),
                "penalty": "Worker may file at National Labour Commission (NLC) - FREE.",
            },
        ],
        "tenancy": [
            {
                "statute": "Ghana Rent Act, 1963 (Act 220)",
                "section": "Section 8",
                "title": "Rent Increase Limits",
                "text": (
                    "Rent may only be increased at lease renewal with at least "
                    "90 days written notice. Increase must not exceed 25% of "
                    "the current rent in a single adjustment."
                ),
                "penalty": "Tenant may file at Rent Tribunal (Accra) - FREE.",
            },
        ],
    },
    "Kenya": {
        "labor": [
            {
                "statute": "Employment Act, 2007 (Kenya)",
                "section": "Section 45",
                "title": "Protection Against Unfair Termination",
                "text": (
                    "No employer shall terminate the employment of an employee "
                    "unfairly. A termination is unfair if the employer fails to "
                    "prove a valid and fair reason connected with the employee's "
                    "capacity, conduct, or operational requirements."
                ),
                "penalty": "Employee may claim up to 12 months wages as compensation.",
            },
        ],
        "contract": [
            {
                "statute": "Law of Contract Act, Cap 23 (Kenya)",
                "section": "Section 14",
                "title": "Unconscionable Contracts",
                "text": (
                    "A contract or clause that is unconscionable — meaning "
                    "grossly unfair and one-sided — may be declared void by "
                    "the court. Standard commercial practice in the industry "
                    "is used as benchmark."
                ),
                "penalty": "Aggrieved party may apply to court to void the unfair clause.",
            },
        ],
    },
}

# All topics present in the database (for validation)
ALL_TOPICS = {"labor", "tenancy", "consumer", "contract", "family", "criminal"}


def search_legal_database(country: str, topic: str, keyword: str = "") -> dict:
    """Search African legal statutes by country and topic.

    Use this tool when the user asks about their legal rights, whether
    something is legal/illegal, or what the law says about a topic.

    Args:
        country: The African country (e.g. "Nigeria", "Ghana", "Kenya").
        topic:   Legal topic — one of: labor, tenancy, consumer, contract, family, criminal.
        keyword: Optional keyword to narrow results (e.g. "salary deduction", "eviction").

    Returns:
        A dict with matching statutes and provisions, or an error message.
    """
    country_data = LEGAL_DATABASE.get(country)
    if not country_data:
        return {
            "found": False,
            "message": f"No legal data available for '{country}'. Available countries: {', '.join(LEGAL_DATABASE.keys())}.",
        }

    topic_data = country_data.get(topic.lower())
    if not topic_data:
        available = ", ".join(country_data.keys())
        return {
            "found": False,
            "message": f"No data for topic '{topic}' in {country}. Available topics: {available}.",
        }

    # If a keyword is provided, filter results
    results = topic_data
    if keyword:
        kw = keyword.lower()
        results = [
            entry for entry in topic_data
            if kw in entry["text"].lower() or kw in entry["title"].lower()
        ]

    if not results:
        return {
            "found": False,
            "message": f"No results matching '{keyword}' under {country} → {topic}.",
        }

    return {
        "found": True,
        "country": country,
        "topic": topic,
        "results": results,
        "count": len(results),
    }
