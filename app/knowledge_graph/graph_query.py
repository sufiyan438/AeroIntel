# import re

# from app.knowledge_graph.neo4j_service import Neo4jService

# class GraphQuery:
#     def __init__(self):
#         self.db = Neo4jService()

#     def query(self, question: str):
#         report = self.extract_report(question)
#         if report is None:
#             return "No report ID found in the question."

#         #Airline
#         if "airline" in question.lower():
#             result = self.db.execute(
#                 """
#                 MATCH (r:Report {id:$id})
#                 -[:OPERATED_BY]->
#                 (a:Airline)
#                 RETURN a.name AS answer
#                 """,
#                 {
#                     "id": report
#                 }
#             )

#         #Aircraft
#         elif "aircraft" in question.lower():
#             result = self.db.execute(
#                 """
#                 MATCH (r:Report {id:$id})
#                 -[:INVOLVES]->
#                 (a:Aircraft)

#                 RETURN a.name AS answer
#                 """,
#                 {"id": report}
#             )

#         #Keywords
#         elif "keyword" in question.lower():
#             result = self.db.execute(
#                 """
#                 MATCH (r:Report {id:$id})
#                 -[:HAS_KEYWORD]->
#                 (k:Keyword)

#                 RETURN k.name AS answer
#                 """,
#                 {"id": report}
#             )

#         else:
#             return "Graph query not supported."

#         answers = [row["answer"] for row in result]
#         if not answers:
#             return "No information found."

#         return "\n".join(answers)


#     def extract_report(self, question):
#         match = re.search(r"AIR\d+", question.upper())
#         if match:
#             return match.group()

#         return None

import re

from app.knowledge_graph.neo4j_service import Neo4jService


class GraphQuery:

    def __init__(self):
        self.db = Neo4jService()

    def query(self, question: str):

        question_lower = question.lower()

        report = self.extract_report(question)

        airline = self.extract_airline(question)

        aircraft = self.extract_aircraft(question)

        # -------------------------------------------------
        # 1. Report -> Airline
        # Example:
        # What airline is associated with AIR2504?
        # -------------------------------------------------

        if report and "airline" in question_lower:

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:OPERATED_BY]->
                (a:Airline)

                RETURN a.name AS answer
                """,
                {
                    "id": report
                }
            )

        # -------------------------------------------------
        # 2. Report -> Aircraft
        # Example:
        # What aircraft is involved in AIR2602?
        # -------------------------------------------------

        elif report and "aircraft" in question_lower:

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:INVOLVES]->
                (a:Aircraft)

                RETURN a.name AS answer
                """,
                {
                    "id": report
                }
            )

        # -------------------------------------------------
        # 3. Report -> Keywords
        # Example:
        # What keywords are associated with AIR2504?
        # -------------------------------------------------

        elif report and "keyword" in question_lower:

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:HAS_KEYWORD]->
                (k:Keyword)

                RETURN k.name AS answer
                """,
                {
                    "id": report
                }
            )

        # -------------------------------------------------
        # 4. Airline -> Aircraft
        # Example:
        # Which aircraft is associated with Alaska Airlines?
        # -------------------------------------------------

        elif airline and "aircraft" in question_lower:

            result = self.db.execute(
                """
                MATCH (r:Report)
                -[:OPERATED_BY]->
                (airline:Airline {name:$airline})

                MATCH (r)
                -[:INVOLVES]->
                (aircraft:Aircraft)

                RETURN DISTINCT aircraft.name AS answer
                """,
                {
                    "airline": airline
                }
            )

        # -------------------------------------------------
        # 5. Airline -> Reports
        # Example:
        # Which reports are associated with Alaska Airlines?
        # -------------------------------------------------

        elif airline and (
            "report" in question_lower
            or "reports" in question_lower
        ):

            result = self.db.execute(
                """
                MATCH (r:Report)
                -[:OPERATED_BY]->
                (a:Airline {name:$airline})

                RETURN DISTINCT r.id AS answer
                """,
                {
                    "airline": airline
                }
            )

        # -------------------------------------------------
        # 6. Aircraft -> Reports
        # Example:
        # Which reports involve CRJ700?
        # -------------------------------------------------

        elif aircraft and (
            "report" in question_lower
            or "reports" in question_lower
        ):

            result = self.db.execute(
                """
                MATCH (r:Report)
                -[:INVOLVES]->
                (a:Aircraft {name:$aircraft})

                RETURN DISTINCT r.id AS answer
                """,
                {
                    "aircraft": aircraft
                }
            )

        else:
            return "Graph query not supported."

        # -------------------------------------------------
        # Format Results
        # -------------------------------------------------

        answers = [
            row["answer"]
            for row in result
        ]

        if not answers:
            return "No information found."

        return "\n".join(answers)

    # -----------------------------------------------------
    # Extract Report ID
    # -----------------------------------------------------

    def extract_report(self, question):

        match = re.search(
            r"\bAIR\d+\b",
            question.upper()
        )

        if match:
            return match.group()

        return None

    # -----------------------------------------------------
    # Extract Airline
    # -----------------------------------------------------

    def extract_airline(self, question):

        result = self.db.execute(
            """
            MATCH (a:Airline)
            RETURN a.name AS name
            """
        )

        question_lower = question.lower()

        for row in result:

            name = row["name"]

            if name.lower() in question_lower:
                return name

        return None

    # -----------------------------------------------------
    # Extract Aircraft
    # -----------------------------------------------------

    def extract_aircraft(self, question):

        result = self.db.execute(
            """
            MATCH (a:Aircraft)
            RETURN a.name AS name
            """
        )

        question_lower = question.lower()

        for row in result:

            name = row["name"]

            if name.lower() in question_lower:
                return name

        return None