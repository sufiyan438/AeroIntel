from typing import TypedDict


class GraphState(TypedDict):

    question: str
    scope: str

    # Retrieval strategy selected by the planner
    route: str

    answer: str
    top_k: int

    # Retrieved evidence
    documents: list
    graph_evidence: list

    # Agentic workflow fields
    evidence_sufficient: bool
    retry_count: int
    recovery_action: str