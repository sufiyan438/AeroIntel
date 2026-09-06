from app.langgraph.workflow import AeroWorkflow
from app.langgraph.evaluator import EvidenceEvaluator


workflow = AeroWorkflow()
evaluator = EvidenceEvaluator()


questions = [
    # Should be sufficient
    "What aircraft were involved in AIR2602?",

    # Important test: current retrieval is known to retrieve
    # the wrong historical accident
    "What was the probable cause of AIR2602?",

    # Should be sufficient
    "What aircraft were involved in AIR2602 and explain the major findings of the accident?"
]


for question in questions:

    print("\n" + "=" * 100)
    print("QUESTION:")
    print(question)

    state = {
        "question": question,
        "scope": "Aviation Database",
        "route": "",
        "answer": "",
        "top_k": 5,
        "documents": [],
        "graph_evidence": [],
        "evidence_sufficient": False,
        "retry_count": 0
    }

    result = workflow.app.invoke(state)

    evaluation = evaluator.evaluate(
        question=result["question"],
        route=result["route"],
        answer=result["answer"],
        documents=result.get("documents", []),
        graph_evidence=result.get("graph_evidence", [])
    )

    print("\nROUTE:")
    print(result["route"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nEVIDENCE SUFFICIENT:")
    print(evaluation["sufficient"])

    print("\nEVALUATOR REASON:")
    print(evaluation["reason"])