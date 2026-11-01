from agent.inventory_agent import (
    ask_agent,
    structured_llm
)

from schemas.inventory_schema import InventoryReport


question = """
Generate a complete inventory report.
Use the available inventory tools to retrieve:
1. Low-stock items
2. Pending deliveries
3. Inventory received this month

Then generate a structured report.
"""

# First, retrieve data through our existing agent
inventory_data = ask_agent(question)

print("Raw inventory data:")
print(inventory_data)

# Convert the retrieved data into structured output
result = structured_llm.invoke(f"""
Convert the following inventory data into the InventoryReport schema.

Use only the provided data. Do not invent information.

Inventory data:
{inventory_data}
""")

print("\nStructured Inventory Report:")
print(result)

print("\nSummary:", result.summary)