import json

from langchain_core.messages import ToolMessage

from app.llm import LLMService
from app.langgraph.tool_state import ToolAgentState


class ToolEvidenceEvaluator:

    def __init__(self):
        self.llm = LLMService().get_control_llm()

    def evaluate(self, state: ToolAgentState):

        question = state["question"]
        answer = state.get("answer", "")

        # Collect only evidence actually returned by tools
        evidence = []

        for message in state.get("messages", []):
            if isinstance(message, ToolMessage):

                # Ignore synthetic messages produced by our duplicate guard
                if message.content.startswith("Tool call blocked:"):
                    continue

                evidence.append(message.content)

        evidence_text = "\n\n---\n\n".join(evidence)

        if not evidence_text:
            return {
                "sufficient": False,
                "reason": "No retrieval evidence was returned by the tools."
            }

        prompt = f"""
You are evaluating retrieval quality in an aviation RAG system.

Your task is to determine whether the RETRIEVED EVIDENCE contains
enough information to answer the user's original question.

Question:
{question}

Retrieved Evidence:
{evidence_text}

Generated Answer:
{answer}

IMPORTANT:

Evaluate the evidence itself, not whether the generated answer is safe
or reasonable.

If the generated answer says:
"I don't know based on the provided documents."

that does NOT mean the evidence is sufficient.

If the requested fact or information is missing from the retrieved
evidence, return sufficient=false.

Return sufficient=true ONLY when the retrieved evidence contains enough
information to answer every important part of the original question.

For compound questions, every requested part must be supported.

Also ensure that the generated answer does not introduce factual claims
that are absent from the retrieved evidence.

Return ONLY valid JSON:

{{
  "sufficient": true,
  "reason": "short explanation"
}}
"""

        response = self.llm.invoke(prompt)

        try:
            result = json.loads(response.content)

            return {
                "sufficient": result.get("sufficient", False) is True,
                "reason": result.get("reason", "")
            }

        except (json.JSONDecodeError, TypeError):
            return {
                "sufficient": False,
                "reason": "Evaluator returned an invalid response."
            }

    def evaluate_state(self, state: ToolAgentState):

        result = self.evaluate(state)

        print("\nEvidence Evaluation:")
        print("Sufficient:", result["sufficient"])
        print("Reason:", result["reason"])

        return {
            **state,
            "evidence_sufficient": result["sufficient"]
        }