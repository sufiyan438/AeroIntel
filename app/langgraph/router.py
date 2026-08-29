# class QueryRouter:
#     """
#     Decides where a query should be routed.

#     Routes:
#     - metadata
#     - vector
#     - graph
#     """

#     def __init__(self):
#         self.metadata_keywords = [
#             "page",
#             "pages",
#             "title",
#             "author",
#             "created",
#             "date",
#             "filename",
#             "report id",
#             "pdf"
#         ]

#         self.graph_keywords = [
#             "relationship",
#             "related",
#             "airline",
#             "aircraft",
#             "manufacturer",
#             "airport",
#             "operator",
#             "compare",
#             "connection",
#             "linked"
#         ]

#     def route(self, question: str, scope: str):
#         question = question.lower()
        
#         if scope == "Uploaded Documents":
#             return "vector"

#         #Metadata route
#         if any(word in question for word in self.metadata_keywords):
#             return "metadata"

#         #Knowledge graph route
#         if any (word in question for word in self.graph_keywords):
#             return "graph"

#         #Default Vector search
#         return "vector"

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

            # Report -> Airline
            r"\b(what|which)\s+airline\b.*\b(associated|related|operated|linked)\b",

            # Report -> Aircraft / Airline -> Aircraft
            r"\b(what|which)\s+aircraft\b.*\b(associated|involved|related|linked)\b",

            # Report -> Keywords
            r"\b(what|which)\s+keywords?\b.*\b(associated|related|linked)\b",

            # Airline/Aircraft -> Report
            r"\b(what|which)\s+reports?\b.*\b(associated|involve|involves|related|linked)\b"
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