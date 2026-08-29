from typing import TypedDict

class GraphState(TypedDict):
    question: str
    scope: str
    route: str
    answer: str
    # documents: str
    top_k: int
    documents:list