from tools.inventory_tools import get_low_stock_items

result = get_low_stock_items.invoke({})

print("Low stock products:")
print(result)