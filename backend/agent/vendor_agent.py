
from langchain_ollama import ChatOllama

from tools.inventory_tools import get_pending_deliveries


# Vendor specialist tool
VENDOR_TOOLS = [
    get_pending_deliveries,
]


# Specialized LLM
llm = ChatOllama(
    model="qwen3:4b",
    temperature=0,
)

vendor_llm = llm.bind_tools(VENDOR_TOOLS)


# System instructions
VENDOR_SYSTEM_PROMPT = """
You are a Vendor Specialist Agent in an Inventory AI Analyst system.

Your responsibilities:
- Analyze vendor and supplier information.
- Identify pending deliveries.
- Report delivery statuses.
- Answer vendor-related questions using database information.

Rules:
- Use tools whenever database information is required.
- Never invent vendor or delivery information.
- Answer clearly and concisely.
- Focus only on vendor and supplier-related queries.
- Do not execute inventory modifications.
- You are ONLY responsible for vendor-related information.
- Do not mention limitations of other specialists or tools.
- Do not discuss low-stock analysis or inventory stock levels.
- Answer only the specific vendor question assigned to you.
"""


def vendor_agent(state: dict):

    messages = state["messages"]

    # Step 1: Ask LLM to decide whether to call a tool
    response = vendor_llm.invoke(
        [
            {"role": "system", "content": VENDOR_SYSTEM_PROMPT},
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
                tool for tool in VENDOR_TOOLS
                if tool.name == tool_name
            )

            tool_result = selected_tool.invoke(tool_args)

            from langchain_core.messages import ToolMessage

            tool_messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

        # Step 3: Generate final response using tool results
        final_response = vendor_llm.invoke(
            [
                {"role": "system", "content": VENDOR_SYSTEM_PROMPT},
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


from agent.multi_agent_state import MultiAgentState


def vendor_agent_node(state: MultiAgentState):

    result = vendor_agent(state)

    final_message = result["messages"][-1]

    return {
        "messages": [final_message],
        "vendor_result": final_message.content,
        "agent_results": [
            {"vendor": final_message.content}
        ],
    }
