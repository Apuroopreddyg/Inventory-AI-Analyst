
from agent.vendor_agent import vendor_agent
from langchain_core.messages import HumanMessage

state = {
    "messages": [
        HumanMessage(content="Which vendors have pending deliveries?")
    ]
}

result = vendor_agent(state)

print("\nVendor Agent Response:")
print(result["messages"][-1].content)

print("\nTool Calls:")
print(result["messages"][-1].tool_calls)
