
from agent.inventory_agent import inventory_agent_node
from agent.multi_agent_state import MultiAgentState
from langchain_core.messages import HumanMessage

state: MultiAgentState = {
    "messages": [
        HumanMessage(content="Show low-stock items")
    ],
    "next_agent": "inventory",
    "agent_result": ""
}

result = inventory_agent_node(state)

print("\nAgent Result:")
print(result["agent_result"])

print("\nNext Agent:")
print(result["next_agent"])
