
from langchain.messages import HumanMessage

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from agent.inventory_hitl_graph import (
    create_inventory_hitl_graph
)


question = "Which products are running low on stock?"


with SqliteSaver.from_conn_string("inventory_hitl.sqlite") as checkpointer:

    graph = create_inventory_hitl_graph(checkpointer)

    config = {
        "configurable": {
            "thread_id": "inventory-hitl-001"
        }
    }

    # Start the graph
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=question)],
            "pending_action": {},
            "approval_status": ""
        },
        config=config
    )

    # Check if approval is required
    if "__interrupt__" in result:

        print("\n--- HUMAN APPROVAL REQUIRED ---")

        for interruption in result["__interrupt__"]:
            print(interruption.value)

        decision = input(
            "\nEnter decision (approve/reject): "
        ).strip().lower()

        if decision not in ["approve", "reject"]:
            print("Invalid decision. Please run the test again.")
        else:
            result = graph.invoke(
                Command(resume=decision),
                config=config
            )

    print("\n--- FINAL RESPONSE ---")
    print(result["messages"][-1].content)
