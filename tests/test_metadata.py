from app.retrieval.metadata_service import MetadataService


def test_report_id_match():
    metadata = MetadataService()

    result = metadata.get_best_match(
        "Tell me about AIR2504"
    )

    assert result is not None
    assert result["report_id"] == "AIR2504"


def test_airline_match():
    metadata = MetadataService()

    result = metadata.get_best_match(
        "Tell me about Alaska Airlines"
    )

    assert result is not None
    assert result["report_id"] == "AIR2504"


def test_generic_question_has_no_match():
    metadata = MetadataService()

    result = metadata.get_best_match(
        "What causes aviation accidents?"
    )

    assert result is None