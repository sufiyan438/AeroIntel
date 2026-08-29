from app.knowledge_graph.graph_query import GraphQuery


def test_report_airline():
    graph = GraphQuery()

    result = graph.query(
        "What airline is associated with AIR2504?"
    )

    assert "Alaska Airlines" in result


def test_report_aircraft():
    graph = GraphQuery()

    result = graph.query(
        "What aircraft is involved in AIR2602?"
    )

    assert "CRJ700" in result
    assert "UH-60" in result