"""
Tool: detect_jurisdiction
==========================
Detects the user's country, legal jurisdiction, and relevant court system
from contextual clues in their message (currency, city names, slang, etc.).

This tool feeds into the Prompt Engineering section — once the country is
detected, the system prompt switches to that country's legal framework.

Presentation example:
    User:  "My oga no gree pay me since March"
    Agent: calls detect_jurisdiction(user_message="My oga no gree pay me since March")
    Tool detects Nigeria (Pidgin English) → agent uses Nigerian system prompt.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Detection rules: markers that indicate a specific country
# ---------------------------------------------------------------------------

COUNTRY_MARKERS: dict[str, dict] = {
    "Nigeria": {
        "currencies": ["naira", "₦", "ngn"],
        "cities": [
            "lagos", "abuja", "kano", "ibadan", "port harcourt",
            "enugu", "benin city", "kaduna", "owerri", "calabar",
        ],
        "slang": [
            "oga", "wahala", "palaver", "no gree", "chop",
            "wetin", "abeg", "na so", "sabi", "pikin",
        ],
        "legal_terms": [
            "nigerian labor act", "fccpc", "national industrial court",
            "lagos tenancy", "nigeria", "nigerian",
        ],
        "language_hint": "Nigerian English / Pidgin",
        "default_currency": "NGN (₦)",
    },
    "Ghana": {
        "currencies": ["cedi", "cedis", "ghs", "gh₵", "₵"],
        "cities": [
            "accra", "kumasi", "tamale", "cape coast", "takoradi",
            "tema", "ho", "sunyani", "koforidua",
        ],
        "slang": ["chale", "charley", "herh", "ei", "bronya"],
        "legal_terms": [
            "ghana labour act", "act 651", "rent tribunal",
            "national labour commission", "ghana", "ghanaian",
        ],
        "language_hint": "Ghanaian English / Twi loanwords",
        "default_currency": "GHS (GH₵)",
    },
    "Kenya": {
        "currencies": ["shilling", "ksh", "kes"],
        "cities": [
            "nairobi", "mombasa", "kisumu", "nakuru", "eldoret",
            "thika", "malindi", "nyeri", "machakos",
        ],
        "slang": ["bana", "sawa", "poa", "fiti", "maze", "mathree"],
        "legal_terms": [
            "employment act 2007", "cap 23", "kenya", "kenyan",
        ],
        "language_hint": "Kenyan English / Sheng",
        "default_currency": "KES (KSh)",
    },
    "South Africa": {
        "currencies": ["rand", "zar", "r"],
        "cities": [
            "johannesburg", "cape town", "durban", "pretoria",
            "soweto", "port elizabeth", "bloemfontein",
        ],
        "slang": ["eish", "yoh", "shame", "braai", "lekker", "ja"],
        "legal_terms": [
            "labour relations act", "ccma", "basic conditions",
            "south africa", "south african",
        ],
        "language_hint": "South African English",
        "default_currency": "ZAR (R)",
    },
    "Tanzania": {
        "currencies": ["tanzanian shilling", "tzs"],
        "cities": [
            "dar es salaam", "dodoma", "arusha", "mwanza",
            "zanzibar", "mbeya",
        ],
        "slang": ["bongo", "mambo", "poa", "karibu"],
        "legal_terms": [
            "employment and labour relations act",
            "tanzania", "tanzanian",
        ],
        "language_hint": "Swahili / Tanzanian English",
        "default_currency": "TZS",
    },
}


def detect_jurisdiction(user_message: str, stated_country: str = "") -> dict:
    """Detect the user's country and legal jurisdiction from their message.

    Use this tool at the START of a conversation to figure out which
    country's law applies, so the agent can use the correct system prompt
    and legal database.

    Args:
        user_message:   The user's message text (may contain city names,
                        currency, slang, or explicit country mention).
        stated_country: If the user explicitly said their country, pass it here.

    Returns:
        A dict with detected country, confidence, and jurisdiction details.
    """
    # If user explicitly stated their country, use it
    if stated_country:
        stated = stated_country.strip().title()
        if stated in COUNTRY_MARKERS:
            info = COUNTRY_MARKERS[stated]
            return {
                "detected_country": stated,
                "confidence": "HIGH",
                "method": "user stated explicitly",
                "currency": info["default_currency"],
                "language_hint": info["language_hint"],
            }
        return {
            "detected_country": stated,
            "confidence": "MEDIUM",
            "method": "user stated (not in detailed database)",
            "currency": "Unknown",
            "language_hint": "Standard English",
            "note": f"{stated} is not yet in our detailed legal database. Responses may be less specific.",
        }

    # Auto-detect from message content
    msg_lower = user_message.lower()
    scores: dict[str, dict] = {}

    for country, markers in COUNTRY_MARKERS.items():
        matches = []

        for currency in markers["currencies"]:
            if currency in msg_lower:
                matches.append(f"currency: {currency}")

        for city in markers["cities"]:
            if city in msg_lower:
                matches.append(f"city: {city}")

        for term in markers["slang"]:
            if term in msg_lower:
                matches.append(f"slang: {term}")

        for term in markers["legal_terms"]:
            if term in msg_lower:
                matches.append(f"legal term: {term}")

        if matches:
            scores[country] = {
                "score": len(matches),
                "matches": matches,
                "currency": markers["default_currency"],
                "language_hint": markers["language_hint"],
            }

    if not scores:
        return {
            "detected_country": "Unknown",
            "confidence": "LOW",
            "method": "no markers detected",
            "suggestion": "Please specify your country so I can give accurate legal advice.",
            "supported_countries": list(COUNTRY_MARKERS.keys()),
        }

    # Pick highest-scoring country
    best_country = max(scores, key=lambda c: scores[c]["score"])
    best = scores[best_country]

    confidence = "HIGH" if best["score"] >= 3 else "MEDIUM" if best["score"] >= 2 else "LOW"

    return {
        "detected_country": best_country,
        "confidence": confidence,
        "method": "auto-detected from message",
        "evidence": best["matches"],
        "currency": best["currency"],
        "language_hint": best["language_hint"],
        "other_possibilities": {
            c: {"score": s["score"], "matches": s["matches"]}
            for c, s in scores.items() if c != best_country
        } or None,
    }
