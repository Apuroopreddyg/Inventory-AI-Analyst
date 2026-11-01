from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage
from schemas.inventory_schema import InventoryReport

llm = ChatOllama(
    model="qwen3:4b",
    temperature=0
)

from langchain.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage
)

SYSTEM_PROMPT = """
You are an Inventory AI Analyst for a business.

Your responsibilities:
- Analyze inventory data provided by tools.
- Answer questions accurately using tool results.
- Identify low-stock products and pending deliveries.
- Summarize inventory transactions.

Rules:
- Be concise, clear, and professional.
- Use bullet points or tables when appropriate.
- Never invent inventory data.
- Never make assumptions about missing data.
- If the tool returns an empty list, simply state that no records were found.
- Do not add unnecessary explanations or generic recommendations.
- Only recommend actions when the data clearly supports them.
"""

from tools.inventory_tools import (
    get_low_stock_items,
    get_pending_deliveries,
    get_monthly_inventory
)

TOOLS = {
    "get_low_stock_items": get_low_stock_items,
    "get_pending_deliveries": get_pending_deliveries,
    "get_monthly_inventory": get_monthly_inventory
}

llm_with_tools = llm.bind_tools(
    list(TOOLS.values())
)

structured_llm = llm.with_structured_output(InventoryReport)


def ask_agent(question):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question)
    ]

    max_iterations = 5

    for iteration in range(max_iterations):

        # Step 1: Invoke the LLM
        try:
            response = llm_with_tools.invoke(messages)

        except Exception as error:
            print(f"LLM Error: {error}")
            return "Sorry, I couldn't process your request."

        # Step 2: Store the LLM response
        messages.append(response)

        # Step 3: Check if the LLM requested tools
        if not response.tool_calls:
            return response.content

        # Step 4: Execute requested tools
        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            # Step 5: Validate the tool name
            if tool_name not in TOOLS:

                tool_result = f"Error: Unknown tool '{tool_name}'."

            else:

                # Step 6: Execute tool safely
                try:
                    tool_result = TOOLS[tool_name].invoke(tool_args)

                except Exception as error:
                    print(f"Tool Error ({tool_name}): {error}")

                    tool_result = (
                        f"Error executing {tool_name}. "
                        "The data could not be retrieved."
                    )

            # Step 7: Return result to the LLM
            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call_id
                )
            )

    # Step 8: Maximum iteration limit
    return "I couldn't complete the analysis within the allowed steps."

