from agent.inventory_graph import ask_inventory_graph


question = "Which products are currently low in stock?"

response = ask_inventory_graph(question)

print("\nAgent Response:")
print(response)