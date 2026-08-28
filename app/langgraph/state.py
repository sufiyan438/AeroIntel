from typing import TypedDict

class GraphState(TypedDict):
    question: str
    scope: str
    route: str
    answer: str
    documents: str