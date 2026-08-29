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


from app.langgraph.workflow import AeroWorkflow


class RAGEngine:

    def __init__(self):
        self.workflow = AeroWorkflow()

    def ask(self, question: str, scope="Both", top_k=5):
        state = {
            "question": question,
            "scope": scope,
            "top_k": top_k,
            "route": "",
            "answer": "",
            "documents": []
        }

        result = self.workflow.app.invoke(state)

        return (
            result["answer"],
            result["documents"]
        )