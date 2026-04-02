# Tool Use Module — Documentation

> **Author:** Larry (Tool Use Section)
> **Module:** `tools/`
> **Dependencies:** None (pure Python — no external packages required)

---

## Overview

This module implements **5 legal tools** that the AI agent can call during a conversation with a citizen. Instead of the LLM guessing or hallucinating legal information, it calls these tools to retrieve real statutes, analyze documents, find precedents, and generate actionable outputs.

This is the **Tool Use** concept from the presentation — the agent decides *when* to call a tool, *which* tool to call, and *chains* multiple tools together to solve the user's problem.

### How Tool Use Works (Conceptually)

```
User asks a question
        │
        ▼
Agent (LLM) reads the question
        │
        ▼
Agent decides which tool(s) to call
        │
        ├──► detect_jurisdiction("My oga no gree pay me in Lagos")
        │         └──► Returns: Nigeria (HIGH confidence)
        │
        ├──► search_legal_database("Nigeria", "labor", "salary deduction")
        │         └──► Returns: Nigerian Labor Act Section 12
        │
        ├──► find_similar_cases("salary deducted for being late")
        │         └──► Returns: Musa v. Al-Bashir Enterprises (2021)
        │
        └──► generate_complaint("unpaid wages", "Nigeria", ...)
                  └──► Returns: Complaint letter + filing instructions
        │
        ▼
Agent combines all tool results into a clear, cited response
```

The key insight: the **agent chooses** which tools to use based on the user's question. A simple rights question might only need `search_legal_database`. A contract review chains `analyze_contract` → `search_legal_database` → `generate_complaint`.

---

## File Structure

```
tools/
├── __init__.py               # Package entry point — exports ALL_TOOLS list
├── legal_search.py           # Tool 1: search_legal_database
├── contract_analyzer.py      # Tool 2: analyze_contract
├── case_search.py            # Tool 3: find_similar_cases
├── complaint_generator.py    # Tool 4: generate_complaint
├── jurisdiction_detector.py  # Tool 5: detect_jurisdiction
└── TOOLS_DOCUMENTATION.md    # This file
```

---

## Tool 1: `search_legal_database`

**File:** `tools/legal_search.py`

**Purpose:** Looks up actual statutes, acts, and legal provisions for African countries. This is the core reference tool — when a citizen asks "Is X legal?", the agent calls this tool to ground its answer in real law.

**Function signature:**
```python
def search_legal_database(country: str, topic: str, keyword: str = "") -> dict
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `country` | str | Yes | African country (e.g. "Nigeria", "Ghana", "Kenya") |
| `topic` | str | Yes | Legal topic: labor, tenancy, consumer, contract, family, criminal |
| `keyword` | str | No | Optional keyword to narrow results (e.g. "salary deduction") |

**Example call & result:**
```python
>>> search_legal_database("Nigeria", "labor", "deduction")
{
    "found": True,
    "country": "Nigeria",
    "topic": "labor",
    "results": [
        {
            "statute": "Nigerian Labor Act, 2004",
            "section": "Section 12",
            "title": "Permissible Deductions from Wages",
            "text": "No employer shall make any deduction from the wages...",
            "penalty": "Worker may claim full refund plus damages..."
        }
    ],
    "count": 1
}
```

**Presentation scenario:** User asks "My boss deducted ₦10,000 from my salary for being 5 minutes late. Is this allowed?" → Agent calls this tool → Gets Section 12 of the Nigerian Labor Act → Tells user it is ILLEGAL and what to do.

**Countries covered:** Nigeria, Ghana, Kenya
**Topics covered:** labor, tenancy, consumer, contract

---

## Tool 2: `analyze_contract`

**File:** `tools/contract_analyzer.py`

**Purpose:** Analyzes contract text for risky, non-standard, or potentially unfair clauses. Flags issues by risk level (HIGH/MEDIUM/LOW) and suggests safer alternatives.

**Function signature:**
```python
def analyze_contract(contract_text: str, country: str = "Nigeria") -> dict
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contract_text` | str | Yes | Full text of the contract to analyze |
| `country` | str | No | Country whose law applies (default: Nigeria) |

**What it detects:**
| Risky Pattern | Risk Level | Why It's Risky |
|---------------|-----------|----------------|
| "buyer liable for all" | HIGH | Shifts ALL liability to buyer — non-standard |
| "no refund" | HIGH | Eliminates refund rights even for defective goods |
| "waive all rights" | HIGH | Blanket waiver, typically unconscionable |
| "non-compete" | MEDIUM | Can restrict future livelihood |
| "automatic renewal" | MEDIUM | Traps party in unwanted obligations |
| "penalty" | MEDIUM | May be unenforceable if disproportionate |
| "sole discretion" | MEDIUM | Gives one party unchecked power |
| "indemnify" | LOW | Standard but should be mutual |

**Also checks for missing standard sections:** payment terms, delivery, cancellation, dispute resolution, liability, governing law.

**Example call & result:**
```python
>>> analyze_contract("The buyer liable for all losses. No refund permitted.", "Nigeria")
{
    "country": "Nigeria",
    "overall_risk": "HIGH — Do NOT sign without legal review",
    "flagged_clauses": [
        {
            "clause_trigger": "buyer liable for all",
            "risk_level": "HIGH",
            "reason": "Shifts ALL liability to buyer...",
            "suggestion": "Replace with: 'Each party shall be liable...'"
        },
        {
            "clause_trigger": "no refund",
            "risk_level": "HIGH",
            "reason": "Eliminates refund rights...",
            "suggestion": "Add: 'Buyer is entitled to a full refund...'"
        }
    ],
    "flagged_count": 2,
    "missing_sections": ["delivery", "cancellation", "dispute resolution", ...],
    "missing_count": 5
}
```

**Presentation scenario:** Trader in Nairobi uploads a ₦2M fabric purchase agreement → Agent calls this tool → Flags "buyer liable for all losses" as HIGH risk → Agent warns trader and provides negotiation language.

---

## Tool 3: `find_similar_cases`

**File:** `tools/case_search.py`

**Purpose:** Finds past court cases relevant to the user's situation. Searches across multiple countries and topics using keyword relevance scoring.

**Function signature:**
```python
def find_similar_cases(
    description: str,
    country: str = "",
    topic: str = "",
    max_results: int = 3,
) -> dict
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | str | Yes | Plain-language description of the user's situation |
| `country` | str | No | Filter to a specific country |
| `topic` | str | No | Filter by topic (e.g. "wrongful dismissal") |
| `max_results` | int | No | Max cases to return (default 3) |

**Sample cases in the database:**
| Case | Country | Topic | Outcome |
|------|---------|-------|---------|
| Adamu v. Sterling Industries (2020) | Nigeria | Wrongful dismissal | 12 months salary + ₦500,000 damages |
| Okafor v. ElectroMart (2018) | Nigeria | Defective goods | Full refund + ₦50,000 damages |
| Bello v. Skyline Properties (2019) | Nigeria | Illegal eviction | Access restored + ₦200,000 damages |
| Musa v. Al-Bashir Enterprises (2021) | Nigeria | Unpaid wages | Full wages + 10% interest/month |
| Mensah v. Goldfields Corp (2021) | Ghana | Unfair termination | 6 months salary + reinstatement |
| Owusu v. Accra Housing (2022) | Ghana | Rent increase | Increase capped at 25% |
| Wanjiku v. TechStart (2022) | Kenya | Wrongful dismissal | 12 months salary |
| Kamau v. MegaSupply (2020) | Kenya | Unfair contract | Unfair clause voided |

**Example call & result:**
```python
>>> find_similar_cases("I was fired without warning from my job", country="Nigeria")
{
    "found": True,
    "cases": [
        {
            "case_name": "Adamu v. Sterling Industries Ltd (2020)",
            "country": "Nigeria",
            "court": "National Industrial Court",
            "topic": "wrongful dismissal",
            "summary": "Worker dismissed without prior warning...",
            "outcome": "Worker awarded 12 months salary..."
        }
    ],
    "count": 1
}
```

**Presentation scenario:** User says "I was fired without cause" → Agent calls this tool → Returns Adamu v. Sterling (12 months salary awarded) → Agent tells user the likely outcome and what to expect.

**Production upgrade:** Replace keyword matching with **embedding similarity search** (Temitope's section) for semantic matching across languages.

---

## Tool 4: `generate_complaint`

**File:** `tools/complaint_generator.py`

**Purpose:** Generates a formal complaint letter and provides step-by-step filing instructions including where to go, what to bring, fees, and expected timelines.

**Function signature:**
```python
def generate_complaint(
    complaint_type: str,
    country: str,
    user_name: str = "[YOUR NAME]",
    opponent_name: str = "[OPPONENT NAME]",
    facts: str = "",
    topic: str = "",
) -> dict
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `complaint_type` | str | Yes | What happened (e.g. "illegal eviction", "unpaid wages") |
| `country` | str | Yes | Country where the complaint will be filed |
| `user_name` | str | No | Complainant's name |
| `opponent_name` | str | No | Who is being complained about |
| `facts` | str | No | Brief description of what happened |
| `topic` | str | No | Legal topic (auto-detected from complaint_type if omitted) |

**Filing info included per country:**
| Country | Topic | Agency | Fee |
|---------|-------|--------|-----|
| Nigeria | Labor | Ministry of Labor / National Industrial Court | FREE - ₦2,000 |
| Nigeria | Tenancy | Lagos State Housing Court | ₦500 - ₦5,000 |
| Nigeria | Consumer | FCCPC | FREE |
| Ghana | Labor | National Labour Commission | FREE |
| Ghana | Tenancy | Rent Tribunal, Accra | FREE |
| Kenya | Labor | Employment and Labour Relations Court | KSh 1,000 - 5,000 |
| Kenya | Contract | High Court / Small Claims Court | KSh 500 - 5,000+ |

**Output includes:**
1. A ready-to-use **complaint letter** (fill in details and print)
2. **Filing info** — where to submit, fees, documents needed, timeline
3. **Next steps** — numbered checklist of what to do

**Presentation scenario:** User says "I want to file a complaint against my landlord" → Agent calls this tool → Returns a formal letter template + "Submit at Lagos State Housing Court, ₦500 filing fee, bring lease + photos + receipts, expect 8-12 weeks."

---

## Tool 5: `detect_jurisdiction`

**File:** `tools/jurisdiction_detector.py`

**Purpose:** Auto-detects the user's country and legal jurisdiction from contextual clues in their message — currency mentions, city names, local slang/pidgin, and legal terms. Feeds into the system prompt selection (Abayomi's Prompt Engineering section).

**Function signature:**
```python
def detect_jurisdiction(user_message: str, stated_country: str = "") -> dict
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_message` | str | Yes | The user's message text |
| `stated_country` | str | No | If user explicitly said their country |

**Detection markers per country:**
| Country | Currencies | Cities | Slang/Pidgin | Legal Terms |
|---------|-----------|--------|-------------|-------------|
| Nigeria | ₦, naira, NGN | Lagos, Abuja, Kano, Ibadan... | oga, wahala, no gree, abeg... | Nigerian Labor Act, FCCPC... |
| Ghana | GH₵, cedi, GHS | Accra, Kumasi, Tamale... | chale, charley, herh... | Act 651, NLC... |
| Kenya | KSh, KES, shilling | Nairobi, Mombasa, Kisumu... | bana, sawa, poa, maze... | Cap 23, Employment Act 2007... |
| South Africa | R, rand, ZAR | Johannesburg, Cape Town... | eish, yoh, lekker, braai... | CCMA, Labour Relations Act... |
| Tanzania | TZS | Dar es Salaam, Dodoma... | bongo, mambo, karibu... | Employment and Labour Relations Act... |

**Confidence levels:**
- **HIGH** — 3+ markers detected (e.g. city + slang + currency)
- **MEDIUM** — 2 markers detected
- **LOW** — 1 marker or none detected (asks user to clarify)

**Example call & result:**
```python
>>> detect_jurisdiction("My oga no gree pay me salary since March in Lagos")
{
    "detected_country": "Nigeria",
    "confidence": "HIGH",
    "method": "auto-detected from message",
    "evidence": ["city: lagos", "slang: oga", "slang: no gree"],
    "currency": "NGN (₦)",
    "language_hint": "Nigerian English / Pidgin"
}
```

**Presentation scenario:** User writes in Pidgin: "My oga no gree pay me" → Agent calls this tool → Detects Nigeria → Switches to Nigerian legal framework and cites Nigerian statutes (not generic advice).

---

## How to Use These Tools

### Direct import (for testing / notebooks)
```python
from tools import search_legal_database, analyze_contract, find_similar_cases

# Call any tool directly
result = search_legal_database("Nigeria", "labor", "salary")
print(result)
```

### Import the full list
```python
from tools import ALL_TOOLS  # list of all 5 tool functions
```

---

## Wiring Into the Agent (Once Teammates Are Ready)

The tools module is **standalone** — it has no dependency on the agent, RAG, or embeddings modules. Once your teammates have their sections built, here is how to bring everything together.

### Step 1: Samuel (Agents) — Create the agent in `legal_agents/__init__.py`

```python
from agents import Agent, function_tool
from tools import ALL_TOOLS

# Wrap each tool for the SDK
agent_tools = [function_tool(t) for t in ALL_TOOLS]

# Use Abayomi's system prompt here
SYSTEM_PROMPT = """
You are a Pan-African Legal Aid Assistant...
(Abayomi provides the full prompt)
"""

legal_advisor_agent = Agent(
    name="Pan-African Legal Advisor",
    instructions=SYSTEM_PROMPT,
    tools=agent_tools,
)
```

### Step 2: Run the agent

```python
from agents import Runner
from legal_agents import legal_advisor_agent

result = Runner.run_sync(
    legal_advisor_agent,
    "My boss deducted ₦10,000 from my salary for being late. Is this legal?"
)
print(result.final_output)
```

### Step 3: Kelvin (RAG) — Swap sample data for real retrieval

In `tools/legal_search.py`, replace the `LEGAL_DATABASE` dict with a call to the RAG pipeline:

```python
# Before (demo):
results = LEGAL_DATABASE[country][topic]

# After (production):
from rag import retrieve_statutes
results = retrieve_statutes(country=country, topic=topic, query=keyword)
```

### Step 4: Temitope (Embeddings) — Swap keyword matching for vector search

In `tools/case_search.py`, replace the keyword scoring loop with embedding similarity:

```python
# Before (demo):
score = sum(1 for kw in case["keywords"] if kw in desc_lower)

# After (production):
from embeddings import get_similar_cases
results = get_similar_cases(description=description, country=country, top_k=max_results)
```

### Step 5: Abayomi (Prompts) — Use jurisdiction detection in the system prompt

The `detect_jurisdiction` tool returns the user's country. Use this to select the right system prompt:

```python
jurisdiction = detect_jurisdiction(user_message)
country = jurisdiction["detected_country"]

# Load country-specific prompt
system_prompt = load_prompt_for_country(country)  # Abayomi provides this
```

---

## Integration Summary

| Teammate | Section | What They Need From This Module | What They Plug Into |
|----------|---------|-------------------------------|---------------------|
| **Kelvin** | RAG | `search_legal_database` calls their retrieval function | Replace `LEGAL_DATABASE` dict in `legal_search.py` |
| **Temitope** | Embeddings | `find_similar_cases` calls their similarity search | Replace keyword scoring in `case_search.py` |
| **Abayomi** | Prompts | `detect_jurisdiction` returns country for prompt selection | Use output to pick the right system prompt |
| **Samuel** | Agents / MCP | `ALL_TOOLS` list ready to pass to `Agent()` | Wire into `legal_agents/__init__.py` |

### Integration diagram

```
┌──────────────────────────────────────────────────────────┐
│                    AGENT (Samuel)                         │
│         legal_agents/__init__.py                          │
│                                                          │
│   System Prompt (Abayomi)                                │
│         ▲                                                │
│         │ country detected                               │
│         │                                                │
│   ┌─────┴──────────────────────────────────────────┐     │
│   │           TOOLS (Larry — this module)           │     │
│   │                                                 │     │
│   │  detect_jurisdiction ──► search_legal_database  │     │
│   │                              ▲                  │     │
│   │                              │ RAG results      │     │
│   │                         ┌────┴────┐             │     │
│   │                         │ Kelvin  │             │     │
│   │                         │  (RAG)  │             │     │
│   │                         └─────────┘             │     │
│   │                                                 │     │
│   │  find_similar_cases                             │     │
│   │         ▲                                       │     │
│   │         │ embeddings                            │     │
│   │    ┌────┴──────┐                                │     │
│   │    │ Temitope  │                                │     │
│   │    │(Embeddings)│                               │     │
│   │    └───────────┘                                │     │
│   │                                                 │     │
│   │  analyze_contract                               │     │
│   │  generate_complaint                             │     │
│   └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

---

## Testing

All tools can be tested with no external dependencies:

```bash
python3 -c "
from tools import search_legal_database, analyze_contract, find_similar_cases, generate_complaint, detect_jurisdiction

# Test each tool
print(search_legal_database('Nigeria', 'labor', 'deduction'))
print(analyze_contract('The buyer liable for all losses. No refund.'))
print(find_similar_cases('I was fired without warning', country='Nigeria'))
print(generate_complaint('illegal eviction', 'Nigeria'))
print(detect_jurisdiction('My oga no gree pay me in Lagos'))
"
```

---

## Production Upgrades (Future)

| Current (Demo) | Production Upgrade |
|----------------|-------------------|
| `LEGAL_DATABASE` dict in Python | PostgreSQL / vector DB with real digitized statutes |
| Keyword matching in `find_similar_cases` | Embedding similarity search (cosine distance) |
| Pattern matching in `analyze_contract` | NLP clause extraction + fine-tuned classifier |
| Hardcoded filing info in `generate_complaint` | API integration with court systems |
| Keyword detection in `detect_jurisdiction` | Language model classification + IP geolocation |
