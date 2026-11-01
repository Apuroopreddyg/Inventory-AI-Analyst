from agent.inventory_agent import ask_agent

questions = [
    "Give me a complete inventory report covering low-stock items, pending deliveries, and inventory received this month."
]

for question in questions:

    print("\n" + "=" * 50)
    print(question)
    print("=" * 50)

    answer = ask_agent(question)

    print(answer)