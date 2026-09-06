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



    def retrieve_evidence(self, question: str):
        """
        Retrieves structured evidence from Neo4j that can be
        supplied to the LLM as part of a GraphRAG context.
        """

        question_lower = question.lower()

        report = self.extract_report(question)
        airline = self.extract_airline(question)
        aircraft = self.extract_aircraft(question)

        # -------------------------------------------------
        # Report -> Airline
        # -------------------------------------------------

        if report and "airline" in question_lower:

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:OPERATED_BY]->
                (a:Airline)

                RETURN
                    r.id AS report,
                    a.name AS airline
                """,
                {
                    "id": report
                }
            )

            return [
                {
                    "type": "report_airline",
                    "report": row["report"],
                    "airline": row["airline"]
                }
                for row in result
            ]

        # -------------------------------------------------
        # Report -> Aircraft
        # -------------------------------------------------

        elif report and "aircraft" in question_lower:

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:INVOLVES]->
                (a:Aircraft)

                RETURN
                    r.id AS report,
                    a.name AS aircraft
                """,
                {
                    "id": report
                }
            )

            return [
                {
                    "type": "report_aircraft",
                    "report": row["report"],
                    "aircraft": row["aircraft"]
                }
                for row in result
            ]

        # -------------------------------------------------
        # Report -> Keywords
        # -------------------------------------------------

        elif report and "keyword" in question_lower:

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:HAS_KEYWORD]->
                (k:Keyword)

                RETURN
                    r.id AS report,
                    k.name AS keyword
                """,
                {
                    "id": report
                }
            )

            return [
                {
                    "type": "report_keyword",
                    "report": row["report"],
                    "keyword": row["keyword"]
                }
                for row in result
            ]

        # -------------------------------------------------
        # Airline -> Aircraft
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

                RETURN DISTINCT
                    airline.name AS airline,
                    aircraft.name AS aircraft
                """,
                {
                    "airline": airline
                }
            )

            return [
                {
                    "type": "airline_aircraft",
                    "airline": row["airline"],
                    "aircraft": row["aircraft"]
                }
                for row in result
            ]

        # -------------------------------------------------
        # Airline -> Reports
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

                RETURN DISTINCT
                    a.name AS airline,
                    r.id AS report
                """,
                {
                    "airline": airline
                }
            )

            return [
                {
                    "type": "airline_report",
                    "airline": row["airline"],
                    "report": row["report"]
                }
                for row in result
            ]

        # -------------------------------------------------
        # Aircraft -> Reports
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

                RETURN DISTINCT
                    a.name AS aircraft,
                    r.id AS report
                """,
                {
                    "aircraft": aircraft
                }
            )

            return [
                {
                    "type": "aircraft_report",
                    "aircraft": row["aircraft"],
                    "report": row["report"]
                }
                for row in result
            ]




                # -------------------------------------------------
        # Report -> Location
        # -------------------------------------------------

        elif report and (
            "where" in question_lower
            or "location" in question_lower
            or "occur" in question_lower
        ):

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:OCCURRED_AT]->
                (l:Location)

                RETURN
                    r.id AS report,
                    l.name AS location
                """,
                {
                    "id": report
                }
            )

            return [
                {
                    "type": "report_location",
                    "report": row["report"],
                    "location": row["location"]
                }
                for row in result
            ]


        # -------------------------------------------------
        # Report -> Cause
        # -------------------------------------------------

        elif report and (
            "cause" in question_lower
            or "caused" in question_lower
        ):

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:HAS_CAUSE]->
                (c:Cause)

                RETURN
                    r.id AS report,
                    c.name AS cause
                """,
                {
                    "id": report
                }
            )

            return [
                {
                    "type": "report_cause",
                    "report": row["report"],
                    "cause": row["cause"]
                }
                for row in result
            ]



        # -------------------------------------------------
        # Report -> Safety Issues
        # -------------------------------------------------

        elif report and (
            "safety issue" in question_lower
            or "safety issues" in question_lower
        ):

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:HAS_SAFETY_ISSUE]->
                (s:SafetyIssue)

                RETURN
                    r.id AS report,
                    s.name AS issue
                """,
                {
                    "id": report
                }
            )

            return [
                {
                    "type": "report_safety_issue",
                    "report": row["report"],
                    "issue": row["issue"]
                }
                for row in result
            ]

        # -------------------------------------------------
        # Report -> Recommendations
        # -------------------------------------------------

        elif report and (
            "recommendation" in question_lower
            or "recommendations" in question_lower
        ):

            result = self.db.execute(
                """
                MATCH (r:Report {id:$id})
                -[:HAS_RECOMMENDATION]->
                (rec:Recommendation)

                OPTIONAL MATCH (rec)
                -[:DIRECTED_TO]->
                (o:Organization)

                RETURN
                    r.id AS report,
                    rec.text AS recommendation,
                    collect(o.name) AS organizations
                """,
                {
                    "id": report
                }
            )

            return [
                {
                    "type": "report_recommendation",
                    "report": row["report"],
                    "recommendation": row["recommendation"],
                    "organizations": row["organizations"]
                }
                for row in result
            ]

        return []




    def format_evidence(self, evidence):
        if not evidence:
            return "No knowledge graph evidence found."

        lines = []

        for item in evidence:
            evidence_type = item.get("type")

            if evidence_type == "report_aircraft":
                # lines.append(
                #     f"Report {item['report']} involves aircraft {item['aircraft']}."
                # )
                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Report {item['report']} involves aircraft {item['aircraft']}."
                )

            elif evidence_type == "report_airline":
                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Report {item['report']} is associated with airline {item['airline']}."
                )

            elif evidence_type == "report_keyword":
                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Report {item['report']} has keyword {item['keyword']}."
                )

            elif evidence_type == "airline_aircraft":
                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Airline {item['airline']} is associated with aircraft {item['aircraft']}."
                )

            elif evidence_type == "airline_report":
                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Airline {item['airline']} is associated with report {item['report']}."
                )

            elif evidence_type == "aircraft_report":
                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Aircraft {item['aircraft']} is associated with report {item['report']}."
                )

            elif evidence_type == "report_location":
                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Report {item['report']} occurred at {item['location']}."
                )

            elif evidence_type == "report_cause":
                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Report {item['report']} identified cause: {item['cause']}."
                )


            elif evidence_type == "report_safety_issue":
                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Report {item['report']} identified safety issue: {item['issue']}."
                )


            elif evidence_type == "report_recommendation":
                organizations = ", ".join(item["organizations"])

                lines.append(
                    f"[Knowledge Graph: {item['report']}]\n"
                    f"Report {item['report']} recommendation: "
                    f"{item['recommendation']}. "
                    f"Directed to: {organizations}."
                )

        return "\n".join(lines)



    def get_vector_query(self, question: str) -> str:
        """
        Creates a vector-search-focused version of a GraphRAG question
        by removing parts already handled by the knowledge graph.
        """

        question_lower = question.lower()

        report = self.extract_report(question)

        if report and "aircraft" in question_lower:
            markers = [
                " and what ",
                " and explain ",
                " and describe ",
                " and why ",
                " and how ",
            ]

            for marker in markers:
                position = question_lower.find(marker)

                if position != -1:
                    semantic_part = question[position + 5:].strip()

                    semantic_lower = semantic_part.lower()

                    if "major findings" in semantic_lower or "findings" in semantic_lower:
                        return (
                            f"{semantic_part} "
                            f"probable cause conclusions safety issues "
                            f"recommendations findings {report}"
                        )

                    return f"{semantic_part} {report}"

        return question