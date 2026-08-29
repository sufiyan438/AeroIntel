import json

from app.knowledge_graph.neo4j_service import Neo4jService

class GraphBuilder:
    def __init__(self):
        self.db = Neo4jService()

    def build(self, metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            reports = json.load(f)

        for report in reports:
            self.add_report(report)

        print("Knowledge Graph Created Successfully!")

    def add_report(self, report):
        report_id = report["report_id"]
        title = report["title"]
        airline = report.get("airline")
        aircraft = report.get("aircraft")
        keywords = report.get("keywords", [])

        #Report node
        self.db.execute(
            """
            MERGE (r:Report {id:$id})

            SET r.title=$title
            """,
            {
                "id": report_id,
                "title": title
            }
        )

        #Airline
        if airline:
            self.db.execute(
                """
                MERGE (a:Airline {name:$name})
                WITH a
                MATCH (r:Report {id:$id})
                MERGE (r)-[:OPERATED_BY]->(a)
                """,
                {
                    "name": airline,
                    "id": report_id
                }
            )

        #Aircraft
        if aircraft:
            if isinstance(aircraft, str):
                aircraft = [aircraft]

            for plane in aircraft:
                self.db.execute(
                    """
                    MERGE (a:Aircraft {name:$name})
                    WITH a
                    MATCH (r:Report {id:$id})
                    MERGE (r)-[:INVOLVES]->(a)
                    """,
                    {
                        "name": plane,
                        "id": report_id
                    }
                )

        #Keywords
        for keyword in keywords:
            self.db.execute(
                """
                MERGE (k:Keyword {name:$name})
                WITH k
                MATCH (r:Report {id:$id})
                MERGE (r)-[:HAS_KEYWORD]->(k)
                """,
                {
                    "name": keyword,
                    "id": report_id
                }
            )