import json
import os
import sys

# Allow imports from the project root
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

from app.retrieval.retrieval_service import RetrievalService


K = 5


def load_dataset():
    dataset_path = os.path.join(
        os.path.dirname(__file__),
        "eval_dataset.json"
    )

    with open(dataset_path, "r") as file:
        return json.load(file)


def evaluate_question(retriever, item):

    question = item["question"]
    relevant_pages = set(item["relevant_pages"])
    expected_report = item["expected_report"]

    results = retriever.retrieve(
        query=question,
        scope="Aviation Database",
        k=K
    )

    retrieved = []

    for doc, score in results:

        source = os.path.basename(
            doc.metadata.get("source", "")
        )

        page = doc.metadata.get("page")

        retrieved.append({
            "source": source,
            "page": page
        })

    # -----------------------------------------------
    # Determine which retrieved chunks are relevant
    # -----------------------------------------------

    relevance = [
        result["source"] == expected_report
        and result["page"] in relevant_pages
        for result in retrieved
    ]

    # Unique relevant pages retrieved
    retrieved_relevant_pages = {
        result["page"]
        for result in retrieved
        if (
            result["source"] == expected_report
            and result["page"] in relevant_pages
        )
    }

    relevant_retrieved = len(retrieved_relevant_pages)

    # -----------------------------------------------
    # Recall@K
    # -----------------------------------------------

    recall = (
        relevant_retrieved / len(relevant_pages)
        if relevant_pages
        else 0
    )

    # -----------------------------------------------
    # Precision@K
    # -----------------------------------------------

    precision = (
        relevant_retrieved / len(retrieved)
        if retrieved
        else 0
    )

    # -----------------------------------------------
    # Reciprocal Rank
    # -----------------------------------------------

    reciprocal_rank = 0

    for rank, is_relevant in enumerate(relevance, start=1):

        if is_relevant:
            reciprocal_rank = 1 / rank
            break

    # -----------------------------------------------
    # Hit Rate@K
    # -----------------------------------------------

    hit = 1 if relevant_retrieved > 0 else 0

    return {
        "id": item["id"],
        "question": question,
        "category": item["category"],
        "retrieved": retrieved,
        "recall": recall,
        "precision": precision,
        "reciprocal_rank": reciprocal_rank,
        "hit": hit,
    }


def main():

    dataset = load_dataset()

    print(f"\nLoading {len(dataset)} evaluation questions...")

    retriever = RetrievalService()

    results = []

    for index, item in enumerate(dataset, start=1):

        print("\n" + "=" * 80)
        print(
            f"[{index}/{len(dataset)}] "
            f"{item['id']}: {item['question']}"
        )

        result = evaluate_question(
            retriever,
            item
        )

        results.append(result)

        print("\nExpected:")
        print(
            item["expected_report"],
            item["relevant_pages"]
        )

        print("\nRetrieved:")

        for rank, retrieved in enumerate(
            result["retrieved"],
            start=1
        ):
            print(
                f"{rank}. "
                f"{retrieved['source']} "
                f"page={retrieved['page']}"
            )

        print(
            f"\nRecall@{K}: "
            f"{result['recall']:.3f}"
        )

        print(
            f"Precision@{K}: "
            f"{result['precision']:.3f}"
        )

        print(
            f"Reciprocal Rank: "
            f"{result['reciprocal_rank']:.3f}"
        )

    # -----------------------------------------------
    # Aggregate metrics
    # -----------------------------------------------

    count = len(results)

    mean_recall = sum(
        result["recall"]
        for result in results
    ) / count

    mean_precision = sum(
        result["precision"]
        for result in results
    ) / count

    mrr = sum(
        result["reciprocal_rank"]
        for result in results
    ) / count
    hit_rate = sum(
        result["hit"]
        for result in results
    ) / count
    print("\n" + "=" * 80)
    print("FINAL RETRIEVAL EVALUATION")
    print("=" * 80)

    print(f"Questions: {count}")
    print(f"Recall@{K}:    {mean_recall:.3f}")
    print(f"Precision@{K}: {mean_precision:.3f}")
    print(f"MRR:           {mrr:.3f}")
    print(f"Hit Rate@{K}:  {hit_rate:.3f}")


if __name__ == "__main__":
    main()