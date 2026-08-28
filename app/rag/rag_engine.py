from app.retrieval.retrieval_service import RetrievalService
from app.llm import LLMService
from app.rag.prompt_builder import PromptBuilder

class RAGEngine:
    def __init__(self):
        self.retriever = RetrievalService()
        self.llm = LLMService()

    def ask(self, question: str, scope="Aviation Database"):
        results = self.retriever.retrieve(query=question, scope=scope)
        doc = [doc for doc, score in results]
        context = "\n\n".join(
           doc.page_content
           for doc in docs
       )

        prompt = PromptBuilder.build(
           context=context,
           question=question
       )

        response = self.llm.invoke(prompt)

        return response.content, results