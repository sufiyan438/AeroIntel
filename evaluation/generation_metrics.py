import asyncio
import json
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, PROJECT_ROOT)

from langchain_huggingface import HuggingFaceEmbeddings

from ragas.dataset_schema import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import Faithfulness, ResponseRelevancy

from app.llm import LLMService
from app.config.settings import EMBEDDING_MODEL


# --------------------------------------------------
# Paths
# --------------------------------------------------

RESULTS_DIR = os.path.join(
    os.path.dirname(__file__),
    "results"
)

OUTPUT_PATH = os.path.join(
    RESULTS_DIR,
    "ragas_generation_metrics.json"
)


# --------------------------------------------------
# Load generation outputs
# --------------------------------------------------

def load_generation_outputs():

    filenames = [
        "generation_outputs_1_10.json",
        "generation_outputs_11_20.json"
    ]

    outputs = []

    for filename in filenames:

        path = os.path.join(
            RESULTS_DIR,
            filename
        )

        if not os.path.exists(path):
            print(
                f"Warning: {filename} not found. Skipping."
            )
            continue

        with open(path, "r") as file:
            data = json.load(file)

        outputs.extend(data)

    return outputs


# --------------------------------------------------
# Load checkpoint
# --------------------------------------------------

def load_checkpoint():

    if not os.path.exists(OUTPUT_PATH):
        return []

    with open(OUTPUT_PATH, "r") as file:
        data = json.load(file)

    return data.get("results", [])


# --------------------------------------------------
# Average helper
# --------------------------------------------------

def calculate_average(values):

    valid = [
        value
        for value in values
        if value is not None
    ]

    if not valid:
        return None

    return sum(valid) / len(valid)


# --------------------------------------------------
# Save checkpoint
# --------------------------------------------------

def save_results(results):

    faithfulness_scores = [
        item["faithfulness"]
        for item in results
        if item["faithfulness"] is not None
    ]

    answer_relevancy_scores = [
        item["answer_relevancy"]
        for item in results
        if item["answer_relevancy"] is not None
    ]

    summary = {
        "completed_questions": len(results),

        "faithfulness_evaluated":
            len(faithfulness_scores),

        "answer_relevancy_evaluated":
            len(answer_relevancy_scores),

        "average_faithfulness":
            calculate_average(
                faithfulness_scores
            ),

        "average_answer_relevancy":
            calculate_average(
                answer_relevancy_scores
            )
    }

    final_output = {
        "summary": summary,
        "results": results
    }

    with open(
        OUTPUT_PATH,
        "w"
    ) as file:

        json.dump(
            final_output,
            file,
            indent=2
        )


# --------------------------------------------------
# Evaluate one question
# --------------------------------------------------

async def evaluate_question(
    item,
    faithfulness_metric,
    relevancy_metric
):

    question = item["question"]
    answer = item["generated_answer"]
    contexts = item.get("contexts", [])

    sample = SingleTurnSample(
        user_input=question,
        response=answer,
        retrieved_contexts=contexts
    )

    faithfulness = None

    # Faithfulness requires retrieved document evidence.
    if contexts:

        print("Evaluating RAGAS Faithfulness...")

        faithfulness = (
            await faithfulness_metric
            .single_turn_ascore(sample)
        )

        faithfulness = float(faithfulness)

    else:

        print(
            "Skipping Faithfulness "
            "(no captured document context)."
        )

    print("Evaluating RAGAS Answer Relevancy...")

    answer_relevancy = (
        await relevancy_metric
        .single_turn_ascore(sample)
    )

    answer_relevancy = float(
        answer_relevancy
    )

    return {
        "id": item["id"],
        "faithfulness": faithfulness,
        "answer_relevancy": answer_relevancy,
        "has_document_context": bool(contexts)
    }


# --------------------------------------------------
# Main
# --------------------------------------------------

async def main():

    outputs = load_generation_outputs()

    if not outputs:
        print("No generation outputs found.")
        return

    print(
        f"\nLoaded {len(outputs)} generated answers."
    )

    # ----------------------------------------------
    # Existing Groq evaluator
    # ----------------------------------------------

    llm_service = LLMService()

    groq_llm = (
        llm_service.get_control_llm()
    )

    ragas_llm = LangchainLLMWrapper(
        groq_llm
    )

    # ----------------------------------------------
    # Local embeddings
    # ----------------------------------------------

    print(
        "\nLoading local embedding model..."
    )

    langchain_embeddings = (
        HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )
    )

    ragas_embeddings = (
        LangchainEmbeddingsWrapper(
            langchain_embeddings
        )
    )

    # ----------------------------------------------
    # RAGAS metrics
    # ----------------------------------------------

    faithfulness_metric = Faithfulness(
        llm=ragas_llm
    )

    relevancy_metric = ResponseRelevancy(
        llm=ragas_llm,
        embeddings=ragas_embeddings
    )

    # ----------------------------------------------
    # Resume previous run
    # ----------------------------------------------

    results = load_checkpoint()

    completed_ids = {
        item["id"]
        for item in results
    }

    if completed_ids:

        print(
            f"\nResuming checkpoint: "
            f"{len(completed_ids)} "
            f"questions already completed."
        )

    # ----------------------------------------------
    # Evaluation loop
    # ----------------------------------------------

    for index, item in enumerate(
        outputs,
        start=1
    ):

        if item["id"] in completed_ids:

            print(
                f"\nSkipping {item['id']} "
                "(already evaluated)."
            )

            continue

        print("\n" + "=" * 80)

        print(
            f"[{index}/{len(outputs)}] "
            f"{item['id']}"
        )

        try:

            result = await evaluate_question(
                item,
                faithfulness_metric,
                relevancy_metric
            )

        except Exception as error:

            print(
                f"\nEvaluation failed for "
                f"{item['id']}:"
            )

            print(error)

            print(
                "\nExisting results are safe. "
                "Run the script again later "
                "to resume."
            )

            break

        results.append(result)

        # Save immediately after every question.
        save_results(results)

        print(
            f"\nFaithfulness: "
            f"{result['faithfulness']}"
        )

        print(
            f"Answer Relevancy: "
            f"{result['answer_relevancy']}"
        )

        print(
            "\nCheckpoint saved."
        )

        # Groq protection.
        print(
            "Waiting 60 seconds before "
            "next question..."
        )

        time.sleep(60)

    # ----------------------------------------------
    # Final output
    # ----------------------------------------------

    save_results(results)

    faithfulness_scores = [
        item["faithfulness"]
        for item in results
        if item["faithfulness"] is not None
    ]

    relevancy_scores = [
        item["answer_relevancy"]
        for item in results
        if item["answer_relevancy"] is not None
    ]

    print("\n" + "=" * 80)
    print("RAGAS GENERATION EVALUATION")
    print("=" * 80)

    print(
        f"Completed questions: "
        f"{len(results)}/{len(outputs)}"
    )

    if faithfulness_scores:

        print(
            f"Faithfulness: "
            f"{calculate_average(faithfulness_scores):.3f}"
        )

        print(
            f"Faithfulness evaluated: "
            f"{len(faithfulness_scores)}"
        )

    if relevancy_scores:

        print(
            f"Answer Relevancy: "
            f"{calculate_average(relevancy_scores):.3f}"
        )

        print(
            f"Answer Relevancy evaluated: "
            f"{len(relevancy_scores)}"
        )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    asyncio.run(main())