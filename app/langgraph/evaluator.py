import json

from app.llm import LLMService


class EvidenceEvaluator:

    def __init__(self):
        self.llm = LLMService().get_llm()

    def evaluate(
        self,
        question: str,
        route: str,
        answer: str,
        documents: list,
        graph_evidence: list
    ):

        # Build compact evidence information for the evaluator
        document_evidence = []

        for item in documents:
            # Retrieval results are stored as (Document, score)
            if isinstance(item, tuple):
                doc = item[0]
            else:
                doc = item

            document_evidence.append(
                doc.page_content[:1500]
            )

        prompt = f"""
You are an evidence evaluator for an aviation investigation RAG system.

Determine whether the retrieved evidence is sufficient and relevant
to answer the user's question.

Question:
{question}

Retrieval strategy:
{route}

Knowledge Graph Evidence:
{graph_evidence}

Document Evidence:
{document_evidence}

Generated Answer:
{answer}

Evaluate whether the evidence actually supports an answer to the
specific question.

IMPORTANT:

- Do not judge an answer as sufficient merely because it is fluent.
- The retrieved evidence must refer to the correct report, accident,
  aircraft, or entity requested by the user.
- Historical accidents mentioned inside a report must not be confused
  with the accident investigated by that report.
- For graph queries, structured graph evidence can be sufficient by itself.
- For metadata queries, a valid metadata answer can be sufficient by itself.
- For vector queries, document evidence must contain information relevant
  to the specific semantic question.
- For hybrid queries, both the structured and semantic portions of the
  question should be supported.
- If the evidence is irrelevant, misleading, incomplete, or refers to
  a different accident, mark it insufficient.

Return ONLY valid JSON in this exact format:

{{
    "sufficient": true,
    "reason": "short explanation"
}}
"""

        response = self.llm.invoke(prompt)

        try:
            decision = json.loads(response.content)

            return {
                "sufficient": bool(
                    decision.get("sufficient", False)
                ),
                "reason": decision.get("reason", "")
            }

        except (json.JSONDecodeError, AttributeError):
            return {
                "sufficient": False,
                "reason": "Evaluator response could not be parsed."
            }




    def evaluate_state(self, state):
        evaluation = self.evaluate(
            question=state["question"],
            route=state["route"],
            answer=state["answer"],
            documents=state.get("documents", []),
            graph_evidence=state.get("graph_evidence", [])
        )

        state["evidence_sufficient"] = evaluation["sufficient"]

        print("\nEvidence Evaluator:")
        print("Sufficient:", evaluation["sufficient"])
        print("Reason:", evaluation["reason"])

        return state