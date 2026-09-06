import json

from app.llm import LLMService


class RecoveryPlanner:

    def __init__(self):
        self.llm = LLMService().get_llm()

    def recover(
        self,
        question: str,
        current_route: str,
        documents: list,
        graph_evidence: list,
        retry_count: int
    ):

        # Keep the evidence compact
        document_evidence = []

        for item in documents:

            if isinstance(item, tuple):
                doc = item[0]
            else:
                doc = item

            document_evidence.append(
                doc.page_content[:1000]
            )

        prompt = f"""
You are a recovery planner for an aviation investigation RAG system.

The system attempted to answer a question, but an evidence evaluator
determined that the retrieved evidence was insufficient.

Your job is to decide the best recovery action.

Question:
{question}

Current retrieval strategy:
{current_route}

Retry count:
{retry_count}

Knowledge Graph Evidence:
{graph_evidence}

Document Evidence:
{document_evidence}

Available recovery actions:

retry_vector:
Use when the question requires semantic or narrative information
from the aviation report documents.

retry_graph:
Use when the question can be answered using structured relationships
such as aircraft, airline, location, cause, safety issues,
recommendations, organizations, or keywords.

retry_hybrid:
Use when answering the question requires BOTH structured knowledge
graph information and semantic information from report documents.

abstain:
Use when the available retrieval strategies are unlikely to provide
sufficient evidence, or when another retry would not be useful.

Rules:

- Choose the recovery action based on the information required by
  the question.
- Do NOT switch retrieval strategies merely because the previous
  strategy failed.
- It is valid to retry the same retrieval type when it is still the
  correct retrieval mechanism.
- Use hybrid only when both graph and document evidence are genuinely
  required.
- Prefer abstaining when repeated retrieval is unlikely to improve
  the evidence.
- Do not invent information.

Return ONLY valid JSON in this exact format:

{{
    "action": "retry_vector|retry_graph|retry_hybrid|abstain",
    "reason": "short explanation"
}}
"""

        response = self.llm.invoke(prompt)

        try:
            decision = json.loads(response.content)

            action = decision.get("action", "abstain").lower()
            reason = decision.get("reason", "")

            valid_actions = {
                "retry_vector",
                "retry_graph",
                "retry_hybrid",
                "abstain"
            }

            if action not in valid_actions:
                action = "abstain"

            return {
                "action": action,
                "reason": reason
            }

        except (json.JSONDecodeError, AttributeError):
            return {
                "action": "abstain",
                "reason": "Recovery planner response could not be parsed."
            }