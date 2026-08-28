class QueryRouter:
    """
    Decides where a query should be routed.

    Routes:
    - metadata
    - vector
    - graph
    """

    def __init__(self):
        self.metadata_keywords = [
            "page",
            "pages",
            "title",
            "author",
            "created",
            "date",
            "filename",
            "report id",
            "pdf"
        ]

        self.graph_keywords = [
            "relationship",
            "related",
            "airline",
            "aircraft",
            "manufacturer",
            "airport",
            "operator",
            "compare",
            "connection",
            "linked"
        ]

    def route(self, question: str, scope: str):
        question = question.lower()
        if scope == "Uploaded Documents":
            return "vector"

        #Metadata route
        if any(word in question for word in self.metadata_keywords):
            return "metadata"

        #Knowledge graph route
        if any (word in question for word in self.graph_keywords):
            return "graph"

        #Default Vector search
        return "vector"