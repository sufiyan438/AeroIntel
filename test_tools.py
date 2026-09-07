from app.langgraph.tools import AeroIntelTools


tool_manager = AeroIntelTools()
tools = tool_manager.get_tools()


for tool in tools:
    print("\n" + "=" * 100)
    print("TOOL:", tool.name)
    print("DESCRIPTION:")
    print(tool.description)


metadata_tool = next(
    tool for tool in tools
    if tool.name == "search_metadata"
)

graph_tool = next(
    tool for tool in tools
    if tool.name == "search_knowledge_graph"
)

vector_tool = next(
    tool for tool in tools
    if tool.name == "search_documents"
)


print("\n" + "=" * 100)
print("METADATA TEST")

print(
    metadata_tool.invoke(
        {
            "query": "What is the title of AIR2602?"
        }
    )
)


print("\n" + "=" * 100)
print("GRAPH TEST")

print(
    graph_tool.invoke(
        {
            "query": "What aircraft were involved in AIR2602?"
        }
    )
)


print("\n" + "=" * 100)
print("VECTOR TEST")

print(
    vector_tool.invoke(
        {
            "query": "Explain the major findings of AIR2602.",
            "scope": "Aviation Database",
            "top_k": 3
        }
    )
)