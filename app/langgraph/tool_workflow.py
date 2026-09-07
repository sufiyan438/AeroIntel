from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.llm import LLMService
from app.langgraph.tools import AeroIntelTools
from app.langgraph.tool_state import ToolAgentState
from app.langgraph.tool_evaluator import ToolEvidenceEvaluator

class ToolAeroWorkflow:

    def __init__(self):

        # Existing AeroIntel tools
        self.tools = AeroIntelTools().get_tools()

        # LLM with tool-calling capability
        self.llm = LLMService().get_control_llm()
        self.evaluator = ToolEvidenceEvaluator()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # LangGraph ToolNode automatically executes tool calls
        self.tool_node = ToolNode(self.tools)

        # Build graph
        self.workflow = StateGraph(ToolAgentState)

        self.workflow.add_node("agent", self.agent_node)
        self.workflow.add_node("tool_guard", self.tool_guard_node)
        self.workflow.add_node("tools", self.tool_node)
        self.workflow.add_node("evaluator", self.evaluator.evaluate_state)

        self.workflow.set_entry_point("agent")

        self.workflow.add_conditional_edges(
            "agent",
            self.agent_decision,
            {
                "tools": "tool_guard",
                "evaluate": "evaluator"
            }
        )
        self.workflow.add_conditional_edges(
            "tool_guard",
            self.guard_decision,
            {
                "execute": "tools",
                "blocked": "agent"
            }
        )

        # After a tool executes, return its result to the agent
        self.workflow.add_edge("tools", "agent")
        self.workflow.add_edge("evaluator", END)

        self.app = self.workflow.compile()



    def agent_node(self, state: ToolAgentState):

        if not state.get("messages"):

            system_message = SystemMessage(
                content="""
You are an aviation investigation research agent.

You have access to retrieval tools for the AeroIntel system.

Use search_metadata ONLY for document-level metadata such as:
- report title
- report ID
- PDF filename
- basic document information

Use search_knowledge_graph for structured investigation facts such as:
- aircraft involved
- airlines
- locations
- causes
- safety issues
- recommendations
- organizations
- keywords
- entity relationships

Use search_documents for narrative and semantic information such as:
- major findings
- explanations
- technical details
- chronology
- conclusions
- probable cause
- narrative reasoning

IMPORTANT:

You may call multiple tools.

A compound question may require more than one retrieval source.

After receiving a tool result, determine whether EVERY part of the
original user's question has been answered.

If another retrieval source is necessary, call another tool.

Do not answer from your own knowledge.

When enough evidence has been retrieved, answer using only the
information returned by the tools.

If the tools do not provide enough evidence, say:
"I don't know based on the provided documents."

Do not repeat a retrieval tool for the same information if that tool
has already returned relevant evidence.

For example, if search_documents has already returned evidence for
"major findings of AIR2602", do not call search_documents again with
a slightly different version such as "AIR2602 findings".

Only repeat a tool when the previous tool result was empty, irrelevant,
or clearly insufficient.

Prefer the minimum number of tool calls necessary to answer the
complete question.

CITATION FORMAT:

For evidence returned by search_documents, cite using exactly:
[filename, p. page_number]

Example:
[AIR2602.pdf, p. 328]

For evidence returned by search_knowledge_graph, cite using exactly:
[Knowledge Graph: report_id]

Example:
[Knowledge Graph: AIR2602]

Do not write citations such as:
"Source: Document page 328"
"Source: AIR2602"
"Knowledge-graph entry"

Do not invent line numbers.

Every factual claim derived from retrieved evidence should use the
citation format provided above.
"""
            )

            human_message = HumanMessage(
                content=state["question"]
            )

            messages = [
                system_message,
                human_message
            ]

            response = self.llm_with_tools.invoke(messages)

            if not response.tool_calls:
                state["answer"] = response.content

            return {
                **state,
                "messages": [
                    system_message,
                    human_message,
                    response
                ]
            }

        messages = state["messages"]

        response = self.llm_with_tools.invoke(messages)

        if not response.tool_calls:
            state["answer"] = response.content

        return {
            **state,
            "messages": [response]
        }







    def agent_decision(self, state: ToolAgentState):

        last_message = state["messages"][-1]

        if getattr(last_message, "tool_calls", None):
            return "tools"

        return "evaluate"






    def tool_guard_node(self, state: ToolAgentState):

        last_message = state["messages"][-1]
        executed_tools = list(state.get("executed_tools", []))

        requested_tools = [
            tool_call["name"]
            for tool_call in last_message.tool_calls
        ]

        repeated_tools = [
            tool_name
            for tool_name in requested_tools
            if tool_name in executed_tools
        ]

        if repeated_tools:

            blocked_messages = []

            for tool_call in last_message.tool_calls:

                blocked_messages.append(
                    ToolMessage(
                        content=(
                            f"Tool call blocked: {tool_call['name']} has already "
                            "been executed for this question. Use the evidence "
                            "already returned instead of repeating this retrieval."
                        ),
                        tool_call_id=tool_call["id"]
                    )
                )

            return {
                **state,
                "messages": blocked_messages,
                "tool_execution_allowed": False
            }

        return {
            **state,
            "executed_tools": executed_tools + requested_tools,
            "tool_execution_allowed": True
        }

    def guard_decision(self, state: ToolAgentState):

        if state["tool_execution_allowed"]:
            return "execute"

        return "blocked"