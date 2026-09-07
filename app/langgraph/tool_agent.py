from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import LLMService
from app.langgraph.tools import AeroIntelTools


class ToolAgent:

    def __init__(self):
        self.tools = AeroIntelTools().get_tools()

        self.llm = LLMService().get_llm()

        # Give the model access to the actual tools
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def decide(self, question: str):

        system_prompt = """
You are an aviation investigation research agent.

You have three retrieval tools.

1. search_metadata

Use ONLY for document-level metadata:
- report title
- report ID
- PDF filename
- basic document information

Do NOT use metadata search for structured investigation facts such as
aircraft involved, accident location, causes, safety issues,
recommendations, or organizations.


2. search_documents

Use for semantic and narrative information contained in investigation
report text, including:
- major findings
- explanations
- technical details
- chronology
- conclusions
- probable cause discussion
- narrative reasoning


3. search_knowledge_graph

Use for structured aviation entities and relationships, including:
- aircraft involved in an accident
- airlines
- accident locations
- causes
- safety issues
- recommendations
- organizations
- keywords
- relationships between reports and entities


TOOL SELECTION RULES:

Determine ALL information required to answer the user's complete question.

A question may require multiple tools.

If different parts of the question require different evidence sources,
call every necessary tool rather than selecting only one.

Examples:

"What is the title of AIR2602?"
→ search_metadata

"What aircraft were involved in AIR2602?"
→ search_knowledge_graph

"Explain the major findings of AIR2602."
→ search_documents

"What aircraft were involved in AIR2602 and explain the major findings?"
→ search_knowledge_graph AND search_documents

Do not answer using your own knowledge.
Do not call tools that are unnecessary.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=question)
        ]

        return self.llm_with_tools.invoke(messages)