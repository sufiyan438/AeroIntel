from app.langgraph.planner import AgentPlanner

planner = AgentPlanner()

questions = [
    "What aircraft were involved in AIR2602?",
    "What was the probable cause of AIR2602?",
    "What safety issues were identified in AIR2602?",
    "What recommendations were made in AIR2602?",
    "Where did AIR2602 occur?",
    "What is the title of AIR2602?",
    "Explain the major findings of AIR2602.",
    "What aircraft were involved in AIR2602 and explain the major findings of the accident?"
]

for question in questions:

    print("\n" + "=" * 80)
    print("QUESTION:")
    print(question)

    decision = planner.plan(
        question=question,
        scope="Aviation Database"
    )

    print("\nSTRATEGY:")
    print(decision["strategy"])

    print("\nREASON:")
    print(decision["reason"])