from app.knowledge_graph.graph_query import GraphQuery

graph = GraphQuery()

print(
    graph.query(
        "Which airline operated AIR2504?"
    )
)

print(
    graph.query(
        "Which aircraft was involved in AIR2602?"
    )
)

print(
    graph.query(
        "Show keywords of AIR2504"
    )
)