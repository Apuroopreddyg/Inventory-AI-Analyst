from langchain_ollama import ChatOllama

from tools.inventory_tools import (
    get_low_stock_items,
    get_pending_deliveries,
    get_monthly_inventory
)

llm = ChatOllama(
    model="qwen3:4b"
)

llm_with_tools = llm.bind_tools(
    [
        get_low_stock_items,
        get_pending_deliveries,
        get_monthly_inventory
    ]
)

questions = [
    "Show low stock items",
    "Which vendors have pending deliveries?",
    "Show inventory received this month"
]

for question in questions:

    print("\n" + "=" * 50)
    print("QUESTION:", question)

    response = llm_with_tools.invoke(question)

    print("\nTOOL SELECTED:")

    print(response.tool_calls)