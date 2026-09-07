from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class ToolAgentState(TypedDict):

    question: str
    scope: str

    messages: Annotated[list, add_messages]

    answer: str

    top_k: int

    documents: list
    graph_evidence: list

    evidence_sufficient: bool

    retry_count: int
    recovery_action: str
    executed_tools: list

    tool_execution_allowed: bool