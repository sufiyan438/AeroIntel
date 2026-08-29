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


    # def vector_node(self, state):
    #     question = state["question"]
    #     scope = state["scope"]
    #     results = self.retriever.retrieve(
    #         query=question,
    #         scope=scope
    #     )

    #     docs = [doc for doc, score in results]

    #     context = "\n\n".join(
    #         doc.page_content
    #         for doc in docs
    #     )

    #     prompt = PromptBuilder.build(
    #         context=context,
    #         question=question
    #     )

    #     response = self.llm.invoke(prompt)
    #     state["answer"] = response.content
    #     state["documents"] = results

    #     return state

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

        # context = "\n\n".join(
        #     doc.page_content
        #     for doc in docs
        # )

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

        else:
            state["answer"] = "No matching report found."

        state["documents"] = []
        return state





    def graph_node(self, state):
        question = state["question"]
        answer = self.graph.query(question)
        state["answer"] = answer
        state["documents"] = []
        return state