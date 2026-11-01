from typing import TypedDict

from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage, ToolMessage

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from tools.inventory_tools import (
    get_low_stock_items,
    get_pending_deliveries,
    get_monthly_inventory
)


# Step 1: Define State
class AgentState(TypedDict):
    messages: list


# Step 2: Initialize LLM
llm = ChatOllama(
    model="qwen3:4b",
    temperature=0
)


SYSTEM_PROMPT = """
You are an Inventory AI Analyst.

Use the available tools to retrieve inventory information.
Answer questions accurately using tool results.

Rules:
- Never invent inventory data.
- Be concise and professional.
- Use tools whenever inventory data is required.
"""


# Step 3: Register Tools
TOOLS = [
    get_low_stock_items,
    get_pending_deliveries,
    get_monthly_inventory
]

llm_with_tools = llm.bind_tools(TOOLS)


# Step 4: Create Agent Node
def agent_node(state: AgentState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


# Step 5: Create Routing Function
def route_tools(state: AgentState):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# Step 6: Create Tool Node
tool_node = ToolNode(TOOLS)


# Step 7: Build Graph
graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "agent")

graph_builder.add_conditional_edges(
    "agent",
    route_tools,
    {
        "tools": "tools",
        END: END
    }
)

graph_builder.add_edge("tools", "agent")


# Step 8: Compile
inventory_graph = graph_builder.compile()


# Step 9: Create Function to Ask Agent
def ask_inventory_graph(question: str):

    result = inventory_graph.invoke({
        "messages": [
            HumanMessage(content=question)
        ]
    })

    return result["messages"][-1].content