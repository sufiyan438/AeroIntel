import re


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
            "page count",
            "number of pages",
            "title",
            "author",
            "created",
            "date",
            "filename",
            "report id",
            "pdf"
        ]

        self.graph_patterns = [
            # Existing patterns
            r"\b(what|which)\s+airline\b.*\b(associated|related|operated|linked)\b",
            r"\b(what|which)\s+aircraft\b.*\b(associated|involved|related|linked)\b",
            r"\b(what|which)\s+keywords?\b.*\b(associated|related|linked)\b",
            r"\b(what|which)\s+reports?\b.*\b(associated|involve|involves|related|linked)\b",

            # Rich knowledge graph relationships
            r"\b(what|which)\b.*\b(cause|causes|caused)\b.*\bair\d+\b",
            r"\b(what|which)\b.*\bsafety issues?\b.*\bair\d+\b",
            r"\b(what|which)\b.*\brecommendations?\b.*\bair\d+\b",
            r"\bwhere\b.*\bair\d+\b.*\boccur(?:red)?\b",
    ]

    def route(self, question: str, scope: str):

        question = question.lower()

        # Uploaded documents only use vector retrieval
        if scope == "Uploaded Documents":
            return "vector"

        # -----------------------------
        # Metadata Route
        # -----------------------------

        if any(
            keyword in question
            for keyword in self.metadata_keywords
        ):
            return "metadata"

        # Probable cause should come from the source document,
        # not the summarized Cause nodes in Neo4j.
        if "probable cause" in question:
            return "vector"

        # -----------------------------
        # Graph Route
        # -----------------------------

        if any(
            re.search(pattern, question)
            for pattern in self.graph_patterns
        ):
            return "graph"

        # -----------------------------
        # Default Vector Route
        # -----------------------------

        return "vector"