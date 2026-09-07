from app.langgraph.tool_workflow import ToolAeroWorkflow
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage
)


workflow = ToolAeroWorkflow()


questions = [
    "What aircraft were involved in AIR2602 and explain the major findings of the accident??"
]


for question in questions:

    print("\n" + "=" * 100)
    print("QUESTION:")
    print(question)

    state = {
        "question": question,
        "scope": "Aviation Database",
        "messages": [],
        "answer": "",
        "top_k": 5,
        "documents": [],
        "graph_evidence": [],
        "evidence_sufficient": False,
        "retry_count": 0,
        "recovery_action": "",
        "executed_tools": [],
        "tool_execution_allowed": True
    }

    result = workflow.app.invoke(state)

    print("\nMESSAGE HISTORY:")

    for message in result["messages"]:

        print("\nTYPE:", type(message).__name__)

        if getattr(message, "tool_calls", None):
            print("TOOL CALLS:")
            for tool_call in message.tool_calls:
                print(
                    "-",
                    tool_call["name"],
                    tool_call["args"]
                )

        if message.content:
            print("CONTENT:")
            print(message.content)

    print("\nFINAL ANSWER:")
    print(result["answer"])