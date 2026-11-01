from langchain_ollama import ChatOllama

from tools.inventory_tools import get_low_stock_items


llm = ChatOllama(
    model="qwen3:4b"
)

# Step 1
response = llm.bind_tools(
    [get_low_stock_items]
).invoke(
    "Show low stock items"
)

print("TOOL CALLS:")
print(response.tool_calls)

# Step 2
tool_result = get_low_stock_items.invoke({})

print("\nTOOL RESULT:")
print(tool_result)

# Step 3
final_response = llm.invoke(
    f"""
    User asked:
    Show low stock items

    Tool returned:

    {tool_result}

    Create a clear inventory report.
    """
)

print("\nFINAL RESPONSE:")
print(final_response.content)