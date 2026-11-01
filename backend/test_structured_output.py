from agent.inventory_agent import llm
from schemas.inventory_schema import LowStockItem


structured_llm = llm.with_structured_output(
    LowStockItem
)

result = structured_llm.invoke("""
Analyze this inventory data:

Product: Router
Current stock: 25
Reorder level: 50

Return its inventory status.
""")

print(result)

print("\nProduct:", result.product)
print("Stock:", result.stock)
print("Reorder Level:", result.reorder_level)
print("Status:", result.status)