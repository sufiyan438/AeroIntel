import os

from langchain_core.tools import tool

from app.retrieval.retrieval_service import RetrievalService
from app.retrieval.metadata_service import MetadataService
from app.knowledge_graph.graph_query import GraphQuery


class AeroIntelTools:

    def __init__(self):
        self.retriever = RetrievalService()
        self.metadata = MetadataService()
        self.graph = GraphQuery()

    def get_tools(self):

        @tool
        def search_metadata(query: str) -> str:
            """
            Search aviation report metadata.

            Use this tool ONLY for document-level metadata such as:
            report title, report ID, PDF filename, and basic document information.

            Do NOT use this tool to answer investigation-domain questions about:
            aircraft involved in an accident, accident location, causes,
            safety issues, recommendations, organizations, or relationships
            between aviation entities. Those belong to the knowledge graph.

            Do NOT use this tool for narrative report content such as findings,
            explanations, conclusions, chronology, or technical details.
            """

            report = self.metadata.get_best_match(query)

            if not report:
                return "No matching report metadata found."

            print("\nTool Executed: search_metadata")

            return (
                f"Report ID: {report.get('report_id')}\n"
                f"Title: {report.get('title')}\n"
                f"Airline: {report.get('airline')}\n"
                f"Aircraft: {report.get('aircraft')}\n"
                f"PDF: {report.get('pdf')}"
            )

        @tool
        def search_documents(
            query: str,
            scope: str = "Aviation Database",
            top_k: int = 5
        ) -> str:
            """
            Search aviation investigation report documents using
            semantic vector retrieval.

            Use this tool for narrative or semantic information such as
            findings, explanations, technical details, chronology,
            conclusions, probable cause, or other information contained
            in report text.
            """

            results = self.retriever.retrieve(
                query=query,
                scope=scope,
                k=top_k
            )

            if not results:
                return "No relevant document evidence found."

            evidence = []

            for doc, score in results:

                filename = os.path.basename(
                    doc.metadata.get("source", "Unknown")
                )

                page = doc.metadata.get("page", 0) + 1

                evidence.append(
                    f"[Source: {filename}, Page: {page}]\n"
                    f"{doc.page_content}"
                )
            print("\nTool Executed: search_documents")
            return "\n\n".join(evidence)

        @tool
        def search_knowledge_graph(query: str) -> str:
            """
            Search the Neo4j aviation knowledge graph.

            Use this tool for structured investigation facts and relationships,
            including:
            - aircraft involved in an accident
            - airlines
            - accident locations
            - causes
            - safety issues
            - recommendations
            - organizations
            - keywords
            - relationships between reports and entities

            IMPORTANT:
            The query passed to this tool must describe the specific relationship
            being requested.

            Good queries:
            - "aircraft involved in AIR2602"
            - "location of AIR2602"
            - "causes of AIR2602"
            - "safety issues in AIR2602"
            - "recommendations from AIR2602"

            Do NOT pass only a report ID such as "AIR2602".
            """

            evidence = self.graph.retrieve_evidence(query)

            if not evidence:
                return "No relevant knowledge graph evidence found."

            return self.graph.format_evidence(evidence)

        print("\nTool Executed: search_knowledge_graph")

        return [
            search_metadata,
            search_documents,
            search_knowledge_graph
        ]