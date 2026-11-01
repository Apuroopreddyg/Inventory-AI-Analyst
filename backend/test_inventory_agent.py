
from agent.inventory_agent import inventory_agent
from langchain_core.messages import HumanMessage

state = {
    "messages": [
        HumanMessage(content="Show low-stock items")
    ]
}

result = inventory_agent(state)

print("\nAgent Response:")
print(result["messages"][-1].content)

print("\nTool Calls:")
print(result["messages"][-1].tool_calls)
