"""
Legal AI Bot - Tool Use Module
==============================
This module contains all the tools the legal chatbot agent can invoke.
Each tool is defined as a plain function with type hints and a docstring,
making it compatible with the OpenAI Agents SDK `function_tool` decorator.

Tools available:
    - search_legal_database   : Look up statutes and legal provisions
    - analyze_contract         : Extract and flag risky clauses from contract text
    - find_similar_cases       : Find relevant past court cases
    - generate_complaint       : Generate a complaint letter / court filing template
    - detect_jurisdiction      : Detect country and legal jurisdiction from user context

Usage with OpenAI Agents SDK:
    from agents import Agent, function_tool
    from tools import ALL_TOOLS

    agent = Agent(
        name="Legal Advisor",
        instructions="You are an African legal aid assistant...",
        tools=ALL_TOOLS,
    )
"""

from tools.legal_search import search_legal_database
from tools.contract_analyzer import analyze_contract
from tools.case_search import find_similar_cases
from tools.complaint_generator import generate_complaint
from tools.jurisdiction_detector import detect_jurisdiction

# Ready-made list your teammates can pass straight to an Agent
ALL_TOOLS = [
    search_legal_database,
    analyze_contract,
    find_similar_cases,
    generate_complaint,
    detect_jurisdiction,
]
