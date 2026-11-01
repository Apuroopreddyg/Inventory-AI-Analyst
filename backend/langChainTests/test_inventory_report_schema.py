
from agent.inventory_agent import llm
from schemas.inventory_schema import InventoryReport


structured_llm = llm.with_structured_output(
    InventoryReport
)

inventory_data = """
Low-stock items:
Router: stock 25, reorder level 50
Firewall: stock 10, reorder level 30

Pending deliveries:
Cisco
Juniper

Inventory received this month:
Router: 100 units from Cisco
Switch: 50 units from Juniper
"""

result = structured_llm.invoke(f"""
Generate a structured inventory report
using only the following data.

{inventory_data}
""")

print(result)

print("\nSummary:", result.summary)

print("\nLow-stock items:")
for item in result.low_stock_items:
    print(item.product, item.stock, item.reorder_level)

print("\nPending deliveries:")
for delivery in result.pending_deliveries:
    print(delivery.vendor, delivery.status)

print("\nReceived inventory:")
for item in result.received_inventory:
    print(item.product, item.quantity, item.vendor)
