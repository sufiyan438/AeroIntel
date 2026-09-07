# from app.retrieval.retrieval_service import RetrievalService
# from app.llm import LLMService
# from app.rag.prompt_builder import PromptBuilder

# class RAGEngine:
#     def __init__(self):
#         self.retriever = RetrievalService()
#         self.llm = LLMService().get_llm()

#     def ask(self, question: str, scope="Aviation Database"):
#         results = self.retriever.retrieve(query=question, scope=scope)
#         docs = [doc for doc, score in results]
#         context = "\n\n".join(
#            doc.page_content
#            for doc in docs
#        )

#         prompt = PromptBuilder.build(
#            context=context,
#            question=question
#        )

#         response = self.llm.invoke(prompt)

#         return response.content, results


# from app.langgraph.workflow import AeroWorkflow
# from app.config.settings import TOP_K


# class RAGEngine:

#     def __init__(self):
#         self.workflow = AeroWorkflow()

#     def ask(self, question: str, scope="Both", top_k=TOP_K):
#         state = {
#             "question": question,
#             "scope": scope,
#             "top_k": top_k,
#             "route": "",
#             "answer": "",
#             "documents": []
#         }

#         result = self.workflow.app.invoke(state)

#         return (
#             result["answer"],
#             result["documents"]
#         )





from langchain_core.messages import ToolMessage

from app.langgraph.tool_workflow import ToolAeroWorkflow
from app.config.settings import TOP_K


class RAGEngine:

    def __init__(self):
        self.workflow = ToolAeroWorkflow()

    def ask(self, question: str, scope="Both", top_k=TOP_K):

        state = {
            "question": question,
            "scope": scope,
            "messages": [],
            "answer": "",
            "top_k": top_k,
            "documents": [],
            "graph_evidence": [],
            "evidence_sufficient": False,
            "retry_count": 0,
            "recovery_action": "",
            "executed_tools": [],
            "tool_execution_allowed": True
        }

        result = self.workflow.app.invoke(state)

        document_contexts = []

        for message in result.get("messages", []):
            if (
                isinstance(message, ToolMessage)
                and message.name == "search_documents"
            ):
                document_contexts.append(message.content)


        print(
            "\nTools used for this query:",
            result.get("executed_tools", []),
            flush=True
        )
        # return (
        #     result["answer"],
        #     result.get("documents", [])
        # )

        return (
            result["answer"],
            document_contexts
        )