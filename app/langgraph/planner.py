import json

from app.llm import LLMService


class AgentPlanner:

    def __init__(self):
        self.llm = LLMService().get_llm()

    def plan(self, question: str, scope: str):

        prompt = f"""
You are a retrieval planner for an aviation investigation assistant.

Your job is to decide which retrieval strategy should be used
to answer the user's question.

Available strategies:

metadata:
Use ONLY for document-level metadata such as:
- title
- filename
- report ID
- page count
- basic document information

graph:
Use when ALL requested information exists as structured
relationships in the knowledge graph.

The knowledge graph directly supports:
- report -> aircraft
- report -> airline
- report -> location
- report -> cause
- report -> safety issue
- report -> recommendation
- recommendation -> organization
- report -> keyword
- airline -> reports
- aircraft -> reports

IMPORTANT:
Recommendations and safety issues are stored directly in the
knowledge graph. Questions asking only for these should use graph,
not vector.

vector:
Use when the answer requires semantic or narrative information
from the report text that is NOT directly represented in the
knowledge graph.

Examples include:
- probable cause
- explanation of events
- major findings
- conclusions
- technical details
- chronology
- narrative reasoning

hybrid:
Use ONLY when the question requires BOTH:
1. structured information from the knowledge graph
2. semantic or narrative information from the report documents

Do NOT select hybrid if every requested fact can already be
answered using graph relationships.

Examples:

Question:
"What aircraft were involved in AIR2602?"
Strategy:
graph

Question:
"What was the probable cause of AIR2602?"
Strategy:
vector

Question:
"What safety issues were identified in AIR2602?"
Strategy:
graph

Question:
"What recommendations were made in AIR2602?"
Strategy:
graph

Question:
"Where did AIR2602 occur?"
Strategy:
graph

Question:
"What is the title of AIR2602?"
Strategy:
metadata

Question:
"Explain the major findings of AIR2602."
Strategy:
vector

Question:
"What aircraft were involved in AIR2602 and explain the major findings of the accident?"
Strategy:
hybrid

Scope:
{scope}

Question:
{question}

Return ONLY valid JSON in this exact format:

{{
    "strategy": "metadata|vector|graph|hybrid",
    "reason": "short explanation"
}}
"""

        response = self.llm.invoke(prompt)

        try:
            decision = json.loads(response.content)

            strategy = decision.get("strategy", "vector").lower()
            reason = decision.get("reason", "")

            if strategy not in {
                "metadata",
                "vector",
                "graph",
                "hybrid"
            }:
                strategy = "vector"

            return {
                "strategy": strategy,
                "reason": reason
            }

        except (json.JSONDecodeError, AttributeError):
            return {
                "strategy": "vector",
                "reason": "Planner response could not be parsed."
            }