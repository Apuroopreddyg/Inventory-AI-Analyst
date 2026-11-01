
from langchain_ollama import ChatOllama
from langchain_core.messages import ToolMessage
from tools.inventory_tools import (
    get_low_stock_items,
    get_monthly_inventory,
)
from agent.multi_agent_state import MultiAgentState

# Inventory specialist tools
INVENTORY_TOOLS = [
    get_low_stock_items,
    get_monthly_inventory,
]

# Specialized LLM
llm = ChatOllama(
    model="qwen3:4b",
    temperature=0,
)

# Bind tools to the LLM
inventory_llm = llm.bind_tools(INVENTORY_TOOLS)

# System instructions
INVENTORY_SYSTEM_PROMPT = """
You are an Inventory Specialist Agent.

Your responsibilities:
- Analyze inventory stock levels.
- Identify low-stock products.
- Provide inventory details.
- Analyze inventory received this month.

Rules:
- Use tools whenever database information is required.
- Never invent inventory data.
- Answer clearly and concisely.
- Do not handle vendor analysis or delivery management.
- Do not execute inventory modifications or purchases.
- You are ONLY responsible for inventory-related information.
- Do not mention limitations of other specialists or tools.
- Do not discuss pending deliveries or vendor analysis.
- Answer only the specific inventory question assigned to you.
"""


def inventory_agent(state: dict):

    messages = state["messages"]

    # Step 1: Ask LLM to decide which tool to call
    response = inventory_llm.invoke(
        [
            {"role": "system", "content": INVENTORY_SYSTEM_PROMPT},
            *messages,
        ]
    )

    # Step 2: Execute requested tools
    if response.tool_calls:

        tool_messages = []

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            selected_tool = next(
                tool for tool in INVENTORY_TOOLS
                if tool.name == tool_name
            )

            tool_result = selected_tool.invoke(tool_args)

            tool_messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

        # Step 3: Send tool results back to LLM
        final_response = inventory_llm.invoke(
            [
                {"role": "system", "content": INVENTORY_SYSTEM_PROMPT},
                *messages,
                response,
                *tool_messages,
            ]
        )

        return {
            "messages": [response, *tool_messages, final_response]
        }

    # No tool required
    return {
        "messages": [response]
    }


def inventory_agent_node(state: MultiAgentState):

    # Pass the shared conversation state to our specialist
    result = inventory_agent(state)

    # Extract the specialist's final response
    final_message = result["messages"][-1]

    return {
        "messages": [final_message],
        "inventory_result": final_message.content,
        "agent_results": [
            {"inventory": final_message.content}
        ],
    }
