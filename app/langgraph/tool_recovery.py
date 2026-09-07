import json

from app.llm import LLMService
from app.langgraph.tool_state import ToolAgentState


class ToolRecoveryPlanner:

    def __init__(self):
        self.llm = LLMService().get_control_llm()

    def plan(self, state: ToolAgentState):

        question = state["question"]
        answer = state.get("answer", "")
        executed_tools = state.get("executed_tools", [])

        prompt = f"""
You are the recovery planner for an aviation RAG agent.

The agent attempted to answer a question, but an evidence evaluator
determined that the retrieved evidence was insufficient.

Question:
{question}

Current Answer:
{answer}

Tools already executed:
{executed_tools}

Available retrieval tools:

search_metadata
- report title
- report ID
- PDF filename
- basic document metadata

search_knowledge_graph
- aircraft
- airlines
- locations
- causes
- safety issues
- recommendations
- organizations
- structured relationships

search_documents
- major findings
- explanations
- technical details
- chronology
- conclusions
- probable cause
- narrative information

Choose ONE recovery action.

Possible actions:

retry_metadata
retry_graph
retry_documents
abstain

Choose a retry only if another retrieval attempt could reasonably
provide the missing evidence.

Choose abstain if the requested information is unlikely to exist
in the available sources.

Return ONLY valid JSON:

{{
  "action": "retry_documents",
  "reason": "short explanation"
}}
"""

        response = self.llm.invoke(prompt)

        try:
            result = json.loads(response.content)

            action = result.get("action", "abstain")

            allowed_actions = {
                "retry_metadata",
                "retry_graph",
                "retry_documents",
                "abstain"
            }

            if action not in allowed_actions:
                action = "abstain"

            return {
                "action": action,
                "reason": result.get("reason", "")
            }

        except (json.JSONDecodeError, TypeError):
            return {
                "action": "abstain",
                "reason": "Recovery planner returned an invalid response."
            }


    def plan_state(self, state: ToolAgentState):

        result = self.plan(state)

        print("\nRecovery Planning:")
        print("Action:", result["action"])
        print("Reason:", result["reason"])

        return {
            **state,
            "recovery_action": result["action"]
        }