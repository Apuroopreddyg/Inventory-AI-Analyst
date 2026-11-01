from tools.inventory_tools import get_pending_deliveries

result = get_pending_deliveries.invoke({})

print("Pending deliveries:")
print(result)