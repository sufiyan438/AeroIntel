from app.langgraph.tool_agent import ToolAgent


agent = ToolAgent()

questions = [
    "What aircraft were involved in AIR2602?",
    "Explain the major findings of AIR2602.",
    "What is the title of AIR2602?",
    "What aircraft were involved in AIR2602 and explain the major findings of the accident?"
]


for question in questions:

    print("\n" + "=" * 100)
    print("QUESTION:")
    print(question)

    response = agent.decide(question)

    print("\nTOOL CALLS:")

    if response.tool_calls:

        for tool_call in response.tool_calls:
            print("Tool:", tool_call["name"])
            print("Arguments:", tool_call["args"])

    else:
        print("No tool selected.")

    if response.content:
        print("\nMODEL CONTENT:")
        print(response.content)