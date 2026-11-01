from langchain_ollama import ChatOllama

from tools.inventory_tools import get_low_stock_items

llm = ChatOllama(
    model="qwen3:4b"
)

llm_with_tools = llm.bind_tools(
    [get_low_stock_items]
)

response = llm_with_tools.invoke(
    "Show low stock items"
)

print(response)