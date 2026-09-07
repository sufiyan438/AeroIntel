import os

from app.retrieval.retrieval_service import RetrievalService
from app.rag.prompt_builder import PromptBuilder
from app.llm import LLMService
from app.retrieval.metadata_service import MetadataService
from app.knowledge_graph.graph_query import GraphQuery

class WorkflowNodes:
    def __init__(self):
        self.retriever = RetrievalService()
        self.metadata = MetadataService()
        self.llm = LLMService().get_llm()
        self.graph = GraphQuery()


    def vector_node(self, state):
        question = state["question"]
        scope = state["scope"]
        top_k = state["top_k"]

        results = self.retriever.retrieve(
            query=question,
            scope=scope,
            k=top_k
        )
        docs = [doc for doc, score in results]

        context = "\n\n".join(
    f"""
[Source: {os.path.basename(doc.metadata.get("source", "Unknown"))},
Page: {doc.metadata.get("page", 0) + 1}]

{doc.page_content}
"""
    for doc in docs
)

        prompt = PromptBuilder.build(
            context=context,
            question=question
        )
        response = self.llm.invoke(prompt)

        state["answer"] = response.content
        state["documents"] = results

        return state




    def metadata_node(self, state):
        question = state["question"]
        report = self.metadata.get_best_match(question)

        if report:
            state["answer"] = f"""
    Report ID: {report['report_id']}

    Title: {report['title']}

    Airline: {report['airline']}

    Aircraft: {report['aircraft']}
    """
            state["evidence_sufficient"] = True

        else:
            state["answer"] = "No matching report found."
            state["evidence_sufficient"] = False

        state["documents"] = []
        return state




    def graph_node(self, state):
        question = state["question"]
        answer = self.graph.query(question)
        
        state["answer"] = answer
        state["documents"] = []
        return state




    def graph_rag_node(self, state):

        question = state["question"]
        scope = state["scope"]
        top_k = state["top_k"]
        route = state["route"]

        # 1. Retrieve structured evidence from Neo4j
        graph_evidence = self.graph.retrieve_evidence(question)
        graph_context = self.graph.format_evidence(graph_evidence)

        # --------------------------------------------------
        # PURE GRAPH ROUTE
        # --------------------------------------------------
        if route == "graph":

            print("\nAgent selected PURE GRAPH retrieval")

            combined_context = f"""
    Knowledge Graph Evidence:
    {graph_context}
    """

            results = []

        # --------------------------------------------------
        # HYBRID ROUTE
        # --------------------------------------------------
        elif route == "hybrid":

            print("\nAgent selected HYBRID retrieval")

            # Extract the semantic portion of the question
            # for vector retrieval
            vector_query = self.graph.get_vector_query(question)

            print("GraphRAG Vector Query:")
            print(vector_query)

            results = self.retriever.retrieve(
                query=vector_query,
                scope=scope,
                k=top_k
            )

            docs = [doc for doc, score in results]

            vector_context = "\n\n".join(
                f"""
    [Source: {os.path.basename(doc.metadata.get("source", "Unknown"))},
    Page: {doc.metadata.get("page", 0) + 1}]

    {doc.page_content}
    """
                for doc in docs
            )

            combined_context = f"""
    Knowledge Graph Evidence:
    {graph_context}

    Document Evidence:
    {vector_context}
    """

        else:
            raise ValueError(
                f"graph_rag_node received unsupported route: {route}"
            )

        # 3. Generate grounded answer
        prompt = PromptBuilder.build(
            context=combined_context,
            question=question
        )

        response = self.llm.invoke(prompt)

        state["answer"] = response.content
        state["documents"] = results
        state["graph_evidence"] = graph_evidence

        return state