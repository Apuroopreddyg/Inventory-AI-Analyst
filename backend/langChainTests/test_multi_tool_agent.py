from agent.inventory_agent import llm_with_tools

question = """
Give me a complete inventory report covering:
1. Low-stock items
2. Pending deliveries
3. Inventory received this month
"""

response = llm_with_tools.invoke(question)

print("Tool calls selected by the LLM:\n")

for tool_call in response.tool_calls:
    print(tool_call["name"])