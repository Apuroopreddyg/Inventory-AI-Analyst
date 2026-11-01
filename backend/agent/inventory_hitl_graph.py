
from typing import TypedDict

from langchain_ollama import ChatOllama
from langchain.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage
)
from langchain.tools import tool

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command

from tools.inventory_tools import (
    get_low_stock_items,
    get_pending_deliveries,
    get_monthly_inventory
)


# 1. Define the graph state
class InventoryState(TypedDict):
    messages: list
    pending_action: dict
    approval_status: str


# 2. Initialize the LLM
llm = ChatOllama(
    model="qwen3:4b",
    temperature=0
)



SYSTEM_PROMPT = """
You are an Inventory AI Analyst.

You help users analyze inventory and perform inventory operations.

STRICT TOOL SELECTION RULES:

1. If the user asks about low stock, insufficient stock,
   or products below reorder level:
   call get_low_stock_items.

2. If the user asks about pending deliveries:
   call get_pending_deliveries.

3. If the user asks about inventory received this month:
   call get_monthly_inventory.

4. Call reorder_inventory ONLY when the user explicitly
   requests placing or executing a reorder.

5. Questions asking for information must NEVER trigger
   reorder_inventory.

6. Never perform an action the user did not request.

Answer using the results returned by the tools.
"""



# 3. Define a simulated sensitive tool
@tool
def reorder_inventory(product: str, quantity: int) -> str:
    """Request a reorder of a product for a specified quantity."""
    return (
        f"Reorder executed successfully: "
        f"{quantity} units of {product}."
    )


# 4. Register tools
READ_TOOLS = [
    get_low_stock_items,
    get_pending_deliveries,
    get_monthly_inventory
]

ALL_TOOLS = READ_TOOLS + [reorder_inventory]

llm_with_read_tools = llm.bind_tools(READ_TOOLS)
llm_with_action_tools = llm.bind_tools([reorder_inventory])


# 5. Agent node
def agent_node(state: InventoryState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    question = state["messages"][-1].content.lower()

    if any(keyword in question for keyword in [
        "low stock", "running low", "below reorder level",
        "insufficient stock", "stock shortage"
    ]):
        response = llm_with_read_tools.invoke(messages)

    elif any(keyword in question for keyword in [
        "reorder", "place an order", "purchase", "restock"
    ]):
        response = llm_with_action_tools.invoke(messages)

    else:
        response = llm.invoke(messages)

    pending_action = {}

    if response.tool_calls:
        pending_action = response.tool_calls[0]

    return {
        "messages": [response],
        "pending_action": pending_action
    }


# 6. Routing function
def route_agent(state: InventoryState):

    action = state.get("pending_action", {})

    if not action:
        return END

    if action["name"] == "reorder_inventory":
        return "approval"

    return "read_tools"


# 7. Read-only ToolNode
read_tool_node = ToolNode(READ_TOOLS)


# 8. Human approval node
def approval_node(state: InventoryState):

    action = state["pending_action"]

    decision = interrupt({
        "question": "The agent is requesting an inventory reorder.",
        "tool": action["name"],
        "arguments": action["args"],
        "options": ["approve", "reject"]
    })

    return {
        "approval_status": decision
    }


# 9. Execute approved action
def execute_action_node(state: InventoryState):

    action = state["pending_action"]

    if state["approval_status"] != "approve":

        tool_result = "Reorder rejected. No inventory changes were made."

    else:

        tool_result = reorder_inventory.invoke(
            action["args"]
        )

    tool_message = ToolMessage(
        content=str(tool_result),
        tool_call_id=action["id"]
    )

    return {
        "messages": [tool_message],
        "pending_action": {},
        "approval_status": ""
    }


# 10. Build graph
graph_builder = StateGraph(InventoryState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("read_tools", read_tool_node)
graph_builder.add_node("approval", approval_node)
graph_builder.add_node("execute_action", execute_action_node)

graph_builder.add_edge(START, "agent")

graph_builder.add_conditional_edges(
    "agent",
    route_agent,
    {
        "read_tools": "read_tools",
        "approval": "approval",
        END: END
    }
)

graph_builder.add_edge("read_tools", "agent")
graph_builder.add_edge("approval", "execute_action")
graph_builder.add_edge("execute_action", END)


# 11. Compile with SQLite checkpointer
def create_inventory_hitl_graph(checkpointer):

    return graph_builder.compile(
        checkpointer=checkpointer
    )
