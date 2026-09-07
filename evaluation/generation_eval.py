import json
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, PROJECT_ROOT)

from app.rag.rag_engine import RAGEngine


def load_dataset():
    dataset_path = os.path.join(
        os.path.dirname(__file__),
        "eval_dataset.json"
    )

    with open(dataset_path, "r") as file:
        return json.load(file)


def main():

    # --------------------------------------------------
    # Load only Batch 1: eval_001 to eval_010
    # --------------------------------------------------

    dataset = load_dataset()[10:20]

    print(
        f"\nLoading {len(dataset)} evaluation questions..."
    )

    # --------------------------------------------------
    # Output location
    # --------------------------------------------------

    results_dir = os.path.join(
        os.path.dirname(__file__),
        "results"
    )

    os.makedirs(
        results_dir,
        exist_ok=True
    )

    output_path = os.path.join(
        results_dir,
        "generation_outputs_11_20.json"
    )

    # --------------------------------------------------
    # Resume existing evaluation
    # --------------------------------------------------

    if os.path.exists(output_path):

        with open(output_path, "r") as file:
            results = json.load(file)

        completed_ids = {
            result["id"]
            for result in results
        }

        print(
            f"Found {len(completed_ids)} "
            "previously completed questions."
        )

    else:

        results = []
        completed_ids = set()

    # --------------------------------------------------
    # Initialize RAG Engine
    # --------------------------------------------------

    rag = RAGEngine()

    # --------------------------------------------------
    # Generate answers
    # --------------------------------------------------

    for index, item in enumerate(
        dataset,
        start=1
    ):

        # Skip already-completed questions
        if item["id"] in completed_ids:

            print(
                f"\n[{index}/{len(dataset)}] "
                f"{item['id']} already completed - skipping."
            )

            continue

        question = item["question"]

        print("\n" + "=" * 80)

        print(
            f"[{index}/{len(dataset)}] "
            f"{item['id']}: {question}"
        )

        # --------------------------------------------------
        # Run actual AeroIntel RAG pipeline
        # --------------------------------------------------

        answer, documents = rag.ask(
            question=question,
            scope="Aviation Database",
            top_k=5
        )

        # These are the actual ToolMessage contexts
        # seen by the agent.
        contexts = documents

        result = {
            "id": item["id"],
            "question": question,
            "reference_answer": item["reference_answer"],
            "generated_answer": answer,
            "contexts": contexts,
            "category": item["category"]
        }

        results.append(result)

        # --------------------------------------------------
        # Save checkpoint immediately
        # --------------------------------------------------

        with open(
            output_path,
            "w"
        ) as file:

            json.dump(
                results,
                file,
                indent=2
            )

        print("\nGenerated Answer:")
        print(answer)

        print(
            f"\nRetrieved contexts: "
            f"{len(contexts)}"
        )

        print(
            f"\nCheckpoint saved: "
            f"{len(results)} completed."
        )

        # --------------------------------------------------
        # Groq TPM protection
        # --------------------------------------------------

        # Don't wait after final question
        remaining_questions = [
            q
            for q in dataset
            if q["id"] not in {
                result["id"]
                for result in results
            }
        ]

        if remaining_questions:

            print(
                "\nWaiting 60 seconds "
                "to avoid Groq TPM rate limit..."
            )

            time.sleep(60)

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("GENERATION BATCH COMPLETE")
    print("=" * 80)

    print(
        f"Generated answers: "
        f"{len(results)}/{len(dataset)}"
    )

    print(
        f"Saved to: {output_path}"
    )


if __name__ == "__main__":
    main()