from app.langgraph.workflow import AeroWorkflow

workflow = AeroWorkflow()

question = (
    "What aircraft were involved in AIR2602 "
    "and what safety issues contributed to the accident?"
)

state = {
    "question": question,
    "scope": "Aviation Database",
    "route": "",
    "answer": "",
    "top_k": 5,
    "documents": [],
    "graph_evidence": []
}

result = workflow.app.invoke(state)

print("\nROUTE:")
print(result["route"])

print("\nGRAPH EVIDENCE:")
for item in result.get("graph_evidence", []):
    print(item)

print("\nDOCUMENTS RETRIEVED:")
print(len(result.get("documents", [])))

print("\nANSWER:")
print(result["answer"])