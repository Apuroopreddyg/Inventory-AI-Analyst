
from agent.multi_agent_graph import multi_agent_graph
from langchain_core.messages import HumanMessage


config = {
    "configurable": {
        "thread_id": "memory-test-1"
    }
}

questions = [
    "Which products are low on stock?",
    "Who supplies those products?",
    "What should I reorder?"
]

for question in questions:
    result = multi_agent_graph.invoke(
        {
            "messages": [HumanMessage(content=question)],
            "next_agent": "",
            "agent_result": "",
            "selected_agents": [],
            "inventory_result": "",
            "vendor_result": "",
            "analytics_result": []
        },
        config=config
    )

    print("\nUSER:", question)
    print("AI:", result["agent_result"])
