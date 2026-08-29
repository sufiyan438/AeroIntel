from app.langgraph.router import QueryRouter


def test_graph_route():
    router = QueryRouter()

    assert router.route(
        "What airline is associated with AIR2504?",
        "Aviation Database"
    ) == "graph"


def test_metadata_route():
    router = QueryRouter()

    assert router.route(
        "What is the title of AIR2504?",
        "Aviation Database"
    ) == "metadata"


def test_vector_route():
    router = QueryRouter()

    assert router.route(
        "What caused the aircraft to crash?",
        "Aviation Database"
    ) == "vector"


def test_uploaded_always_vector():
    router = QueryRouter()

    assert router.route(
        "What airline is associated with AIR2504?",
        "Uploaded Documents"
    ) == "vector"