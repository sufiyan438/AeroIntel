import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

class LLMService:
    def __init__(self):
        self.llm = ChatGroq(model="openai/gpt-oss-120b",
                            temperature=0,
                            api_key=os.getenv("GROQ_API_KEY"))

    def get_llm(self):
        return self.llm