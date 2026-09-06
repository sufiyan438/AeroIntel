from app.langgraph.workflow import AeroWorkflow

workflow = AeroWorkflow()

questions = [
    # GRAPH
    "What aircraft were involved in AIR2602?",

    # VECTOR
    "Explain the major findings of AIR2602.",

    # METADATA
    "What is the title of AIR2602?",

    # HYBRID
    "What aircraft were involved in AIR2602 and explain the major findings of the accident?",
    "What was the engine serial number mentioned in AIR2602?"
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
        "retry_count": 0,
        "recovery_action": ""
    }

    result = workflow.app.invoke(state)

    print("\nFINAL ROUTE:")
    print(result["route"])

    print("\nEVIDENCE SUFFICIENT:")
    print(result["evidence_sufficient"])

    print("\nRETRY COUNT:")
    print(result["retry_count"])

    print("\nRECOVERY ACTION:")
    print(result["recovery_action"])

    print("\nGRAPH EVIDENCE:")
    print(result.get("graph_evidence", []))

    print("\nDOCUMENTS RETRIEVED:")
    print(len(result.get("documents", [])))

    print("\nANSWER:")
    print(result["answer"])