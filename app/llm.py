# import os

# from dotenv import load_dotenv
# from langchain_groq import ChatGroq

# class LLMService:
#     def __init__(self):
#         self.llm = ChatGroq(model="openai/gpt-oss-120b",
#                             temperature=0,
#                             api_key=os.getenv("GROQ_API_KEY"))

#     def get_llm(self):
#         return self.llm

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


class LLMService:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        # Large model for final answer generation
        self.generation_llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            api_key=api_key
        )

        # Lightweight model for agent decisions,
        # evaluation and recovery
        self.control_llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0,
            api_key=api_key
        )

    def get_llm(self):
        """
        Keep backward compatibility with the existing application.
        """
        return self.generation_llm

    def get_generation_llm(self):
        return self.generation_llm

    def get_control_llm(self):
        return self.control_llm