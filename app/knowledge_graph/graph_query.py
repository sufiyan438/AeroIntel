import re

from app.knowledge_graph.neo4j_service import Neo4jService

class GraphQuery:
    def __init__(self):
        self.db = Neo4jService()

    def query(self, question: str):
        report = self.extract_report(question)
        if report is None:
            return "No report ID found in the question."

        #Airline
        if "airline" in question.lower():
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

        #Aircraft
        elif "aircraft" in question.lower():
            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:INVOLVES]->
                (a:Aircraft)

                RETURN a.name AS answer
                """,
                {"id": report}
            )

        #Keywords
        elif "keyword" in question.lower():
            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:HAS_KEYWORD]->
                (k:Keyword)

                RETURN k.name AS answer
                """,
                {"id": report}
            )

        else:
            return "Graph query not supported."

        answers = [row["answer"] for row in result]
        if not answers:
            return "No information found."

        return "\n".join(answers)


    def extract_report(self, question):
        match = re.search(r"AIR\d+", question.upper())
        if match:
            return match.group()

        return None