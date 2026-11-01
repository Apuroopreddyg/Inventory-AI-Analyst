
from pyexpat.errors import messages
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage
)
from langchain.tools import tool
import json
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command

from tools.inventory_tools import (
    get_low_stock_items,
    get_pending_deliveries,
    get_monthly_inventory,
    reorder_inventory,
    receive_delivery,
    generate_inventory_report
)


# 1. Define the graph state
class InventoryState(TypedDict):
    messages: Annotated[list, add_messages]
    pending_action: dict
    approval_status: str
    user_question: str
    tool_count: int
    report_data: dict


# 2. Initialize the LLM
llm = ChatOllama(
    model="qwen3:4b",
    temperature=0
)


SYSTEM_PROMPT = """
You are Inventory AI Analyst, an assistant that manages inventory
using MongoDB tools.

CONVERSATION CONTEXT:
- Always consider the entire conversation history.
- Resolve references such as "it", "they", "their", "that product",
  "the previous one", and similar expressions using conversation context.
- For follow-up questions, identify the relevant product, vendor,
  delivery, or inventory item from previous messages.
- Do not treat a follow-up as an unrelated new question.

TOOL USAGE:
- Use get_low_stock_items for low-stock queries.
- Use get_pending_deliveries for pending delivery queries.
- Use get_monthly_inventory for monthly received inventory queries.
- Use reorder_inventory only when the user explicitly requests
  a reorder or purchase.
- Use receive_delivery only when the user explicitly requests
  receiving or marking a specific purchase order as delivered.
- Use tools to retrieve factual inventory information.
- Never invent inventory, product, vendor, or delivery data.
- Use generate_inventory_report when the user requests
  a complete or comprehensive inventory report.
- Do not individually call the report's component tools
  when the complete report workflow is appropriate.

APPROVAL:
- Reorder and receive_delivery are actions that require human approval.
- Never claim an action was completed before tool execution.

RESPONSE:
- Provide concise, natural answers to the user's question.
- Never reveal internal reasoning.
- Never explain why you selected or did not select a tool.
"""


# 3. Define a simulated sensitive tool

from datetime import datetime
from uuid import uuid4

from database.mongodb import db



# 4. Register tools

READ_TOOLS = [
    get_low_stock_items,
    get_pending_deliveries,
    get_monthly_inventory
]

ACTION_TOOLS = [
    reorder_inventory,
    receive_delivery
]

WORKFLOW_TOOLS = [
    generate_inventory_report
]

ALL_TOOLS = READ_TOOLS + ACTION_TOOLS + WORKFLOW_TOOLS

llm_with_read_tools = llm.bind_tools(READ_TOOLS)
llm_with_action_tools = llm.bind_tools(ACTION_TOOLS)
llm_with_workflow_tools = llm.bind_tools(WORKFLOW_TOOLS)


# 5. Agent node


def agent_node(state: InventoryState):

    # Pass the full conversation history to the LLM
    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    question = state.get("user_question", "")

    if not question:
        for message in reversed(state["messages"]):
            if isinstance(message, HumanMessage):
                question = message.content
                break

    print(f"[AGENT] Current question: {question}")

    # Let the LLM choose the appropriate tool using
    # conversation history and tool descriptions
    llm_with_all_tools = llm.bind_tools(ALL_TOOLS)
    print("\n[MEMORY] Messages available to agent:")

    for msg in messages:
        print(f"[MEMORY] {type(msg).__name__}: {msg.content}")
    
    response = llm_with_all_tools.invoke(messages)

    pending_action = {}

    if response.tool_calls:
        pending_action = response.tool_calls[0]

        print("[AGENT] Tool call detected:")
        print(f"[AGENT] Tool name: {pending_action['name']}")
        print(f"[AGENT] Tool arguments: {pending_action['args']}")

    else:
        print("[AGENT] LLM response content:")
        print(response.content)

    return {
        "messages": [response],
        "pending_action": pending_action
    }


# 6. Routing function
def route_agent(state: InventoryState):

    action = state.get("pending_action", {})

    # No tool call: agent has a normal response
    if not action:
        return "response"

    # Human approval required for action tools
    if action["name"] in [
        "reorder_inventory",
        "receive_delivery"
    ]:
        return "approval"

    # Complete report workflow
    if action["name"] == "generate_inventory_report":
        return "workflow"

    # Regular read tools
    return "read_tools"

# 7. Read-only ToolNode
read_tool_node = ToolNode(READ_TOOLS)

def execute_read_tool(state: InventoryState):
    
    tool_count = state.get("tool_count", 0) + 1

    print(f"[STATE] Tools executed so far: {tool_count}")

    tool_call = state["messages"][-1].tool_calls[0]

    print(f"[TOOL] Executing: {tool_call['name']}")

    if tool_call["name"] == "get_monthly_inventory":
        result = get_monthly_inventory.invoke({})

        print("[TOOL] Monthly inventory result:")
        print(result)

        return {
            "messages": [
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
            ],
            "tool_count": tool_count
        }

    # Execute other read-only tools normally
    result = read_tool_node.invoke(state)

    return {
        **result,
        "tool_count": tool_count
    }
    
def execute_workflow_node(state: InventoryState):

    tool_call = state["messages"][-1].tool_calls[0]

    print(f"[WORKFLOW] Executing: {tool_call['name']}")

    result = generate_inventory_report.invoke({})

    tool_message = ToolMessage(
        content=str(result),
        tool_call_id=tool_call["id"]
    )

    return {
        "messages": [tool_message],
        "pending_action": {}
    }
    
def report_node(state: InventoryState):

    report = {
        "low_stock": [],
        "pending_deliveries": [],
        "monthly_received": [],
        "complete_report": ""
    }

    for message in state["messages"]:

        if isinstance(message, ToolMessage):

            # Complete report generated by the workflow
            if message.content.startswith("### Inventory Report"):
                report["complete_report"] = message.content
                break

            # Parse individual inventory tool results
            try:
                result = json.loads(message.content)
            except (json.JSONDecodeError, TypeError):
                continue

            if "get_low_stock_items" in str(message.name):
                report["low_stock"] = result

            elif "get_pending_deliveries" in str(message.name):
                report["pending_deliveries"] = result

            elif "get_monthly_inventory" in str(message.name):
                report["monthly_received"] = result

    print("\n[REPORT NODE] Structured report created:")
    print(report)

    return {"report_data": report}



def response_node(state: InventoryState):

    last_message = state["messages"][-1]

    # If the workflow generated a complete Markdown report
    if isinstance(last_message, ToolMessage) and last_message.content.startswith("### Inventory Report"):
        return {
            "messages": [
                AIMessage(content=last_message.content)
            ]
        }

    # Normal agent response is already correct
    return {}


# 8. Human approval node

def approval_node(state: InventoryState):

    action = state["pending_action"]

    if action["name"] == "reorder_inventory":
        question = "The AI agent is requesting an inventory reorder."

    elif action["name"] == "receive_delivery":
        question = "The AI agent is requesting approval to receive a delivery."

    else:
        question = "The AI agent is requesting approval for an action."

    decision = interrupt({
        "question": question,
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

    if action["name"] == "reorder_inventory":
        tool_result = reorder_inventory.invoke(action["args"])

    elif action["name"] == "receive_delivery":
        tool_result = receive_delivery.invoke(action["args"])

    else:
        tool_result = "Unknown action requested."

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
graph_builder.add_node("read_tools", execute_read_tool)
graph_builder.add_node("approval", approval_node)
graph_builder.add_node("execute_action", execute_action_node)
graph_builder.add_node("response", response_node)
graph_builder.add_node("workflow", execute_workflow_node)

graph_builder.add_edge(START, "agent")

graph_builder.add_conditional_edges(
    "agent",
    route_agent,
    {
        "read_tools": "read_tools",
        "approval": "approval",
        "workflow": "workflow",
        "response": "response"
    }
)

# KEY CHANGE: Return to agent after executing a read tool
graph_builder.add_edge("read_tools", "agent")

# Action flow remains unchanged
graph_builder.add_edge("approval", "execute_action")
graph_builder.add_edge("execute_action", END)
graph_builder.add_edge("response", END)
graph_builder.add_edge("workflow", "response")


# 11. Compile with SQLite checkpointer
def create_inventory_hitl_graph(checkpointer):

    return graph_builder.compile(
        checkpointer=checkpointer
    )
