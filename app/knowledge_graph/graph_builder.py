import json

from app.knowledge_graph.neo4j_service import Neo4jService

class GraphBuilder:
    def __init__(self):
        self.db = Neo4jService()


    #Builds neo4j graph using reports.json
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

        location = report.get("location")
        causes = report.get("causes", [])
        safety_issues = report.get("safety_issues", [])
        recommendations = report.get("recommendations", [])

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





        # Location
        if location:
            self.db.execute(
                """
                MERGE (l:Location {name:$name})
                WITH l
                MATCH (r:Report {id:$id})
                MERGE (r)-[:OCCURRED_AT]->(l)
                """,
                {
                    "name": location,
                    "id": report_id
                }
            )


        # Causes
        for cause in causes:
            self.db.execute(
                """
                MERGE (c:Cause {name:$name})
                WITH c
                MATCH (r:Report {id:$id})
                MERGE (r)-[:HAS_CAUSE]->(c)
                """,
                {
                    "name": cause,
                    "id": report_id
                }
            )


        # Safety Issues
        for issue in safety_issues:
            self.db.execute(
                """
                MERGE (s:SafetyIssue {name:$name})
                WITH s
                MATCH (r:Report {id:$id})
                MERGE (r)-[:HAS_SAFETY_ISSUE]->(s)
                """,
                {
                    "name": issue,
                    "id": report_id
                }
            )


        # Recommendations
        for recommendation in recommendations:
            recommendation_text = recommendation["text"]

            self.db.execute(
                """
                MERGE (rec:Recommendation {text:$text})
                WITH rec
                MATCH (r:Report {id:$id})
                MERGE (r)-[:HAS_RECOMMENDATION]->(rec)
                """,
                {
                    "text": recommendation_text,
                    "id": report_id
                }
            )

            for organization in recommendation.get("directed_to", []):
                self.db.execute(
                    """
                    MERGE (o:Organization {name:$organization})
                    WITH o
                    MATCH (rec:Recommendation {text:$text})
                    MERGE (rec)-[:DIRECTED_TO]->(o)
                    """,
                    {
                        "organization": organization,
                        "text": recommendation_text
                    }
                )