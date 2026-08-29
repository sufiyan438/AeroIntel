from app.retrieval.retrieval_service import RetrievalService


def test_aviation_retrieval():
    retriever = RetrievalService()

    results = retriever.retrieve(
        query="What caused the aviation accident?",
        scope="Aviation Database",
        k=3
    )

    assert len(results) > 0
    assert len(results) <= 3


def test_uploaded_retrieval():
    retriever = RetrievalService()

    results = retriever.retrieve(
        query="What was the probable cause of the air show collision?",
        scope="Uploaded Documents",
        k=3
    )

    assert len(results) <= 3