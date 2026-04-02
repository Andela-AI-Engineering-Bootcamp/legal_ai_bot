"""
Tool: generate_complaint
=========================
Generates a formal complaint letter or court filing template that
the citizen can use to take legal action.

Presentation example:
    User:  "I want to file a complaint against my landlord for illegal eviction."
    Agent: calls generate_complaint(complaint_type="illegal eviction",
                                    country="Nigeria", user_name="...", ...)
    Tool returns a ready-to-use letter → user prints and submits.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Filing info per country (where to submit, fees, requirements)
# ---------------------------------------------------------------------------

FILING_INFO: dict[str, dict[str, dict]] = {
    "Nigeria": {
        "labor": {
            "agency": "Ministry of Labor & Employment / National Industrial Court",
            "filing_fee": "FREE (Ministry) or ₦500-₦2,000 (Court)",
            "documents_needed": ["ID card", "Employment contract/offer letter", "Payslips", "Evidence of violation"],
            "timeline": "4-8 weeks (Ministry), 3-6 months (Court)",
        },
        "tenancy": {
            "agency": "Lagos State Housing Court (or equivalent state court)",
            "filing_fee": "₦500-₦5,000",
            "documents_needed": ["ID card", "Lease/tenancy agreement", "Rent receipts", "Evidence of violation", "Photographs"],
            "timeline": "8-12 weeks",
        },
        "consumer": {
            "agency": "Federal Competition & Consumer Protection Commission (FCCPC)",
            "filing_fee": "FREE",
            "documents_needed": ["ID card", "Receipt of purchase", "Product photos", "Communication with seller"],
            "timeline": "4-8 weeks",
        },
    },
    "Ghana": {
        "labor": {
            "agency": "National Labour Commission (NLC)",
            "filing_fee": "FREE",
            "documents_needed": ["ID card", "Employment contract", "Payslips", "Termination letter"],
            "timeline": "4-6 weeks",
        },
        "tenancy": {
            "agency": "Rent Tribunal, Accra (or regional equivalent)",
            "filing_fee": "FREE",
            "documents_needed": ["ID card", "Tenancy agreement", "Rent receipts", "Notice from landlord"],
            "timeline": "6-10 weeks",
        },
    },
    "Kenya": {
        "labor": {
            "agency": "Employment and Labour Relations Court",
            "filing_fee": "KSh 1,000-5,000",
            "documents_needed": ["ID card", "Employment contract", "Payslips", "Termination letter"],
            "timeline": "3-6 months",
        },
        "contract": {
            "agency": "High Court / Small Claims Court (for amounts under KSh 1M)",
            "filing_fee": "KSh 500-2,000 (Small Claims) or KSh 5,000+ (High Court)",
            "documents_needed": ["ID card", "Contract copy", "Evidence of breach", "Communication records"],
            "timeline": "2-4 months (Small Claims), 6-12 months (High Court)",
        },
    },
}


def generate_complaint(
    complaint_type: str,
    country: str,
    user_name: str = "[YOUR NAME]",
    opponent_name: str = "[OPPONENT NAME]",
    facts: str = "",
    topic: str = "",
) -> dict:
    """Generate a formal complaint letter and filing guide.

    Use this tool when the user wants to take action — file a complaint,
    write a demand letter, or submit a case to a court or agency.

    Args:
        complaint_type: What happened (e.g. "illegal eviction", "unpaid wages",
                        "defective product", "unfair contract").
        country:        Country where the complaint will be filed.
        user_name:      Complainant's name (or placeholder).
        opponent_name:  Name of the person/company being complained about.
        facts:          Brief description of what happened.
        topic:          Legal topic for filing info lookup (labor, tenancy, consumer, contract).

    Returns:
        A dict with the complaint letter text, filing instructions, and required documents.
    """
    if not complaint_type:
        return {"error": "Please specify what you are complaining about."}

    # --- Determine topic if not provided ---
    if not topic:
        type_lower = complaint_type.lower()
        if any(kw in type_lower for kw in ["salary", "wage", "fired", "dismiss", "employer", "work"]):
            topic = "labor"
        elif any(kw in type_lower for kw in ["rent", "evict", "landlord", "tenant", "lease"]):
            topic = "tenancy"
        elif any(kw in type_lower for kw in ["product", "defective", "refund", "purchase", "goods"]):
            topic = "consumer"
        elif any(kw in type_lower for kw in ["contract", "agreement", "supplier", "breach"]):
            topic = "contract"
        else:
            topic = "labor"  # default

    # --- Get filing info ---
    country_info = FILING_INFO.get(country, {})
    filing = country_info.get(topic, {
        "agency": f"Relevant {topic} authority in {country}",
        "filing_fee": "Contact the agency for current fees",
        "documents_needed": ["ID card", "Evidence of violation", "Communication records"],
        "timeline": "Varies — contact agency for estimate",
    })

    # --- Generate the complaint letter ---
    facts_section = facts if facts else f"[Describe the details of the {complaint_type} here]"

    letter = f"""
FORMAL COMPLAINT LETTER
========================

Date: [INSERT DATE]
To: {filing['agency']}

FROM: {user_name}
AGAINST: {opponent_name}

SUBJECT: Formal Complaint — {complaint_type.title()}

Dear Sir/Madam,

I, {user_name}, respectfully submit this formal complaint against
{opponent_name} for the following violation:

COMPLAINT TYPE: {complaint_type.title()}

FACTS OF THE CASE:
{facts_section}

RELIEF SOUGHT:
I respectfully request that the appropriate authority:
1. Investigate this matter promptly
2. Order {opponent_name} to cease the unlawful conduct
3. Award appropriate compensation for damages suffered
4. Take any other action deemed fit under the law

I attach all supporting documents as listed below and am available
for further questioning at your convenience.

Respectfully submitted,

____________________________
{user_name}
[Phone number]
[Address]
""".strip()

    return {
        "complaint_letter": letter,
        "filing_info": {
            "where_to_file": filing["agency"],
            "filing_fee": filing["filing_fee"],
            "documents_needed": filing["documents_needed"],
            "estimated_timeline": filing["timeline"],
        },
        "next_steps": [
            "Fill in your personal details and the date",
            "Attach all supporting documents (receipts, photos, contracts, messages)",
            "Make 3 copies of everything (1 for court, 1 for opponent, 1 for yourself)",
            f"Submit at: {filing['agency']}",
            "Keep your filing receipt — it is proof you submitted",
            "Follow up after 2 weeks if you haven't heard back",
        ],
        "country": country,
        "topic": topic,
    }
