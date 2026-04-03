# Tool Use Module — Documentation

> **Author:** Larry (Tool Use Section)
> **Module:** `tools/`
> **Data Source:** Real Nigerian legal acts from `rag/knowledge-base/`
> **Dependencies:** None (pure Python — no external packages required)

---

## Overview

This module implements **5 legal tools** that the AI agent can call during a conversation with a citizen. Instead of the LLM guessing or hallucinating legal information, it calls these tools to search **real Nigerian statutes** from the knowledge base, analyze documents, find relevant provisions, and generate actionable outputs.

This is the **Tool Use** concept from the presentation — the agent decides *when* to call a tool, *which* tool to call, and *chains* multiple tools together to solve the user's problem.

### Knowledge Base (Source Data)

All tools read from the actual legal documents in `rag/knowledge-base/`:

| File | Act | Content |
|------|-----|---------|
| `Labour Act.md` | Labour Act, 1974 (No. 21) | Wage protection, contracts, termination, hours, leave, recruiting |
| `Tenancy Law.md` | Lagos Tenancy Law, 2011 | Tenant rights, notice periods, eviction, court procedures, mediation |
| `Federal Consumer Act.md` | Federal Competition and Consumer Protection Act, 2018 | Consumer rights, refunds, defective goods, FCCPC enforcement |
| `Consumer Act.md` | Consumer Act | Consumer protection provisions |
| `Food And Drugs Act.md` | Food and Drugs Act | Food/drug manufacturing and sale regulations |
| `Nigeria Constitution 1999.md` | Constitution of the Federal Republic of Nigeria, 1999 | Fundamental rights, citizenship, governance |
| `Tenancy Disputes.md` | Tenancy Disputes (Research) | Academic paper on property dispute resolution |

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
        ├──► search_legal_database(topic="labor", keyword="deduction")
        │         └──► Searches Labour Act.md → Returns Section 5 text
        │
        ├──► find_similar_cases("salary deducted for being late")
        │         └──► Searches knowledge base → Returns Labour Act Sections 5, 11
        │
        └──► generate_complaint("unpaid wages", ...)
                  └──► Returns: Complaint letter citing Labour Act Sections 80-85
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

**Purpose:** Searches the actual Nigerian legal acts in `rag/knowledge-base/` by topic and keyword. Returns real statute text with section numbers.

**Function signature:**
```python
def search_legal_database(topic: str, keyword: str = "", section: str = "") -> dict
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | str | Yes | Legal topic: labor, tenancy, consumer, constitution, food |
| `keyword` | str | No | Keyword to search for (e.g. "deduction", "eviction") |
| `section` | str | No | Specific section number to look up (e.g. "5", "13") |

**Topic-to-file mapping:**
| Topic | Knowledge Base File(s) |
|-------|----------------------|
| `labor` | `Labour Act.md` |
| `tenancy` | `Tenancy Law.md`, `Tenancy Disputes.md` |
| `consumer` | `Federal Consumer Act.md`, `Consumer Act.md` |
| `constitution` | `Nigeria Constitution 1999.md` |
| `food` | `Food And Drugs Act.md` |

**Example call & result:**
```python
>>> search_legal_database("labor", "deduction")
{
    "found": True,
    "topic": "labor",
    "search_term": "deduction",
    "results": [
        {
            "section": "5. Deductions (including deductions for overpayment of wages)",
            "excerpt": "(1) Except where it is expressly permitted by this Act...",
            "source_act": "Labour Act, 1974 (No. 21)",
            "source_file": "Labour Act.md"
        }
    ],
    "count": 1,
    "note": "Excerpts from actual Nigerian legal acts in rag/knowledge-base/."
}
```

**Presentation scenario:** User asks "My boss deducted ₦10,000 from my salary for being 5 minutes late" → Agent calls this tool → Searches `Labour Act.md` → Returns Section 5 which says deductions for fines are prohibited → Agent cites the real statute.

---

## Tool 2: `analyze_contract`

**File:** `tools/contract_analyzer.py`

**Purpose:** Analyzes contract text for risky, non-standard, or potentially unfair clauses. All flags reference real Nigerian law from the knowledge base.

**Function signature:**
```python
def analyze_contract(contract_text: str, country: str = "Nigeria") -> dict
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contract_text` | str | Yes | Full text of the contract to analyze |
| `country` | str | No | Country whose law applies (default: Nigeria) |

**What it detects (with real legal references):**
| Risky Pattern | Risk Level | Legal Reference |
|---------------|-----------|-----------------|
| "buyer liable for all" | HIGH | FCCPA 2018, Section 136 — liability for defective goods |
| "no refund" | HIGH | FCCPA 2018, Section 122 — consumer right to return goods |
| "waive all rights" | HIGH | FCCPA 2018 — prohibits waiving consumer rights |
| "deduction" | MEDIUM | Labour Act 1974, Section 5 — permitted deductions only |
| "non-compete" | MEDIUM | Labour Act 1974, Section 9(6) — freedom to work |
| "automatic renewal" | MEDIUM | Nigerian contract law best practice |
| "penalty" | MEDIUM | Nigerian common law — proportionality requirement |
| "sole discretion" | MEDIUM | Good faith requirement |
| "indemnify" | LOW | Standard but should be mutual |

**Example call & result:**
```python
>>> analyze_contract("The buyer liable for all losses. No refund permitted.")
{
    "country": "Nigeria",
    "overall_risk": "HIGH — Do NOT sign without legal review",
    "flagged_clauses": [...],
    "flagged_count": 2,
    "legal_references": [
        "Federal Competition and Consumer Protection Act, 2018 (Sections 122, 123, 136)",
        "Labour Act, 1974 (Sections 5, 9)",
        "Source: rag/knowledge-base/Federal Consumer Act.md, Labour Act.md"
    ]
}
```

---

## Tool 3: `find_similar_cases`

**File:** `tools/case_search.py`

**Purpose:** Searches the knowledge base for legal provisions relevant to the user's situation. Maps common scenarios (fired, evicted, defective product) to the appropriate acts and finds the most relevant sections.

**Function signature:**
```python
def find_similar_cases(description: str, topic: str = "", max_results: int = 5) -> dict
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | str | Yes | Plain-language description of the user's situation |
| `topic` | str | No | Filter by topic (e.g. "labor", "tenancy") |
| `max_results` | int | No | Max provisions to return (default 5) |

**Scenario mapping (keyword → knowledge base file):**
| User says... | Searches... | For terms... |
|-------------|-------------|-------------|
| "fired", "dismissed" | `Labour Act.md` | termination, notice, dismiss |
| "salary", "deduction" | `Labour Act.md` | wages, payment, deduction |
| "eviction", "landlord" | `Tenancy Law.md` | possession, notice, quit |
| "refund", "defective" | `Federal Consumer Act.md` | refund, return, defective |
| "rights", "arrest" | `Nigeria Constitution 1999.md` | right, freedom, liberty |
| "overtime", "leave" | `Labour Act.md` | overtime, hours, holiday, sick |

**Example call & result:**
```python
>>> find_similar_cases("I was fired without warning from my job")
{
    "found": True,
    "provisions": [
        {
            "section": "11. Termination of contracts by notice",
            "excerpt": "(1) Either party to a contract of employment may terminate...",
            "source_file": "Labour Act.md",
            "source_act": "LABOUR ACT"
        },
        {
            "section": "9. Contracts: general",
            "excerpt": "...",
            "source_file": "Labour Act.md",
            "source_act": "LABOUR ACT"
        }
    ],
    "count": 2,
    "note": "Provisions sourced from actual Nigerian legal acts in rag/knowledge-base/."
}
```

**Production upgrade:** Replace keyword matching with **embedding similarity search** (Temitope's section) using the FAISS vector store already set up in `rag/store.py`.

---

## Tool 4: `generate_complaint`

**File:** `tools/complaint_generator.py`

**Purpose:** Generates a formal complaint letter citing real Nigerian law, with filing procedures derived from the actual statutes.

**Function signature:**
```python
def generate_complaint(
    complaint_type: str,
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
| `user_name` | str | No | Complainant's name |
| `opponent_name` | str | No | Who is being complained about |
| `facts` | str | No | Brief description of what happened |
| `topic` | str | No | Legal topic (auto-detected if omitted) |

**Filing info (from real statutes):**
| Topic | Where to File | Legal Basis |
|-------|--------------|-------------|
| Labor | Ministry of Labor / Magistrate Court (Labour Act Section 80) | Labour Act Sections 80-85 |
| Tenancy | Magistrate Court / High Court Lagos (Tenancy Law Section 2), Citizens Mediation Centre (Section 32) | Lagos Tenancy Law Sections 13, 16, 24-27, 32 |
| Consumer | FCCPC (established under FCCPA Section 3) | FCCPA Sections 17, 18, 122, 136 |
| Constitution | Federal/State High Court | Constitution 1999, Chapter IV |

**Output includes:**
1. A **complaint letter** citing the specific legal basis from the knowledge base
2. **Filing info** — where to submit, documents needed, timeline (from the actual statutes)
3. **Next steps** — numbered checklist

---

## Tool 5: `detect_jurisdiction`

**File:** `tools/jurisdiction_detector.py`

**Purpose:** Auto-detects the user's country and legal jurisdiction from contextual clues in their message — currency mentions, city names, local slang/pidgin, and legal terms.

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
| Country | Currencies | Cities | Slang/Pidgin |
|---------|-----------|--------|-------------|
| Nigeria | ₦, naira, NGN | Lagos, Abuja, Kano... | oga, wahala, no gree, abeg... |
| Ghana | GH₵, cedi, GHS | Accra, Kumasi... | chale, charley... |
| Kenya | KSh, KES | Nairobi, Mombasa... | bana, sawa, poa... |
| South Africa | R, rand, ZAR | Johannesburg, Cape Town... | eish, yoh, lekker... |
| Tanzania | TZS | Dar es Salaam, Dodoma... | bongo, mambo... |

**Note:** The knowledge base currently covers **Nigerian law only**. When the user's country is detected, the tools search Nigerian statutes. Future expansion can add other countries' acts to `rag/knowledge-base/`.

---

## How to Use These Tools

### Direct import (for testing / notebooks)
```python
from tools import search_legal_database, analyze_contract, find_similar_cases

# Search real statutes
result = search_legal_database("labor", "deduction")
print(result)

# Analyze a contract against real Nigerian law
result = analyze_contract("The buyer liable for all losses. No refund.")
print(result)

# Find relevant provisions for a situation
result = find_similar_cases("my landlord locked me out")
print(result)
```

### Import the full list
```python
from tools import ALL_TOOLS  # list of all 5 tool functions
```

---

## Wiring Into the Agent (Once Teammates Are Ready)

The tools module is **standalone** — it reads directly from `rag/knowledge-base/` with no dependency on the agent, RAG pipeline, or embeddings modules. Once teammates have their sections built, here is how to bring everything together.

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

### Step 3: Kelvin (RAG) — Upgrade search with vector retrieval

In `tools/legal_search.py`, the `_search_sections` function currently does keyword search. Replace with the RAG pipeline from `rag/query.py`:

```python
# Before (current — keyword search):
matches = _search_sections(text, search_term)

# After (production — use Kelvin's RAG pipeline):
from rag.query import query_knowledge_base
matches = query_knowledge_base(search_term, topic=topic)
```

### Step 4: Temitope (Embeddings) — Upgrade case search with vector similarity

In `tools/case_search.py`, replace keyword matching with the FAISS store from `rag/store.py`:

```python
# Before (current — keyword scoring):
sections = _find_relevant_sections(text, source["terms"])

# After (production — use embeddings):
from rag.store import load_vector_store
from rag.embeddings import get_embeddings
store = load_vector_store()
results = store.similarity_search(description, k=max_results)
```

### Step 5: Abayomi (Prompts) — Use jurisdiction detection for prompt selection

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
| **Kelvin** | RAG | `search_legal_database` already reads from `rag/knowledge-base/`. Upgrade: swap keyword search for RAG pipeline in `rag/query.py` | `_search_sections()` in `legal_search.py` |
| **Temitope** | Embeddings | `find_similar_cases` already reads from `rag/knowledge-base/`. Upgrade: swap keyword scoring for FAISS similarity from `rag/store.py` | `_find_relevant_sections()` in `case_search.py` |
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
│   │                              │ RAG upgrade      │     │
│   │                         ┌────┴────┐             │     │
│   │                         │ Kelvin  │             │     │
│   │                         │  (RAG)  │             │     │
│   │                         └─────────┘             │     │
│   │                                                 │     │
│   │  find_similar_cases                             │     │
│   │         ▲                                       │     │
│   │         │ embeddings upgrade                    │     │
│   │    ┌────┴──────┐                                │     │
│   │    │ Temitope  │                                │     │
│   │    │(Embeddings)│                               │     │
│   │    └───────────┘                                │     │
│   │                                                 │     │
│   │  analyze_contract (cites FCCPA, Labour Act)     │     │
│   │  generate_complaint (cites Tenancy Law, etc.)   │     │
│   └─────────────────────────────────────────────────┘     │
│                                                          │
│   All tools read from: rag/knowledge-base/*.md           │
└──────────────────────────────────────────────────────────┘
```

---

## Testing

All tools can be tested with no external dependencies (they read the markdown files directly):

```bash
python3 -c "
from tools import search_legal_database, analyze_contract, find_similar_cases, generate_complaint, detect_jurisdiction

# Search real statutes
print(search_legal_database('labor', 'deduction'))

# Analyze contract against real Nigerian law
print(analyze_contract('The buyer liable for all losses. No refund.'))

# Find relevant provisions
print(find_similar_cases('I was fired without warning'))

# Generate complaint with real filing procedures
print(generate_complaint('illegal eviction'))

# Detect jurisdiction
print(detect_jurisdiction('My oga no gree pay me in Lagos'))
"
```

---

## Production Upgrades (Future)

| Current (Working) | Production Upgrade |
|-------------------|-------------------|
| Keyword search through `rag/knowledge-base/*.md` files | Use Kelvin's RAG pipeline with vector retrieval (`rag/query.py`) |
| Keyword scoring in `find_similar_cases` | Use Temitope's FAISS embeddings from `rag/store.py` |
| Pattern matching in `analyze_contract` | NLP clause extraction + fine-tuned classifier |
| Nigerian law only | Add other African countries' acts to `rag/knowledge-base/` |
| Keyword detection in `detect_jurisdiction` | Language model classification + IP geolocation |
