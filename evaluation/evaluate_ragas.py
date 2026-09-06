import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import FactualCorrectness

from app.rag.rag_engine import RAGEngine


load_dotenv()

DATASET_PATH = Path("evaluation/dataset.json")


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    dataset = load_dataset()

    rag = RAGEngine()

    # LLM used by RAGAS to judge correctness
    evaluator_llm = LangchainLLMWrapper(
        ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )
    )

    evaluation_rows = []

    for item in dataset:
        question = item["question"]
        reference = item["reference"]

        answer, docs = rag.ask(
            question,
            scope="Aviation Database",
            top_k=5
        )

        evaluation_rows.append(
            {
                "user_input": question,
                "response": answer,
                "reference": reference
            }
        )

        print("=" * 80)
        print("Question:", question)
        print("Reference:", reference)
        print("Generated:", answer)

    eval_dataset = EvaluationDataset.from_list(evaluation_rows)

    result = evaluate(
        dataset=eval_dataset,
        metrics=[
            FactualCorrectness(llm=evaluator_llm)
        ]
    )

    print("\nRAGAS RESULTS")
    print(result)

    print("\nDETAILED RESULTS")

    df = result.to_pandas()

    print(
        df[
            [
                "user_input",
                "response",
                "reference",
                "factual_correctness(mode=f1)"
            ]
        ].to_string(index=False)
    )