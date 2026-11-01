from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from tools.inventory_tools import (
    get_low_stock_items,
    get_pending_deliveries,
    get_monthly_inventory
)

class InventoryReportState(TypedDict):
    low_stock: list
    pending_deliveries: list
    monthly_received: list
    report: str
    
    
def low_stock_node(state: InventoryReportState):

    result = get_low_stock_items.invoke({})

    print("[REPORT WORKFLOW] Low-stock data fetched:", result)

    return {
        "low_stock": result
    }
    
def pending_deliveries_node(state: InventoryReportState):

    result = get_pending_deliveries.invoke({})

    print("[REPORT WORKFLOW] Pending deliveries fetched:", result)

    return {
        "pending_deliveries": result
    }
    
def monthly_inventory_node(state: InventoryReportState):

    result = get_monthly_inventory.invoke({})

    print("[REPORT WORKFLOW] Monthly inventory fetched:", result)

    return {
        "monthly_received": result
    }
    
from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen3:4b",
    temperature=0
)


def report_generator_node(state: InventoryReportState):

    report_data = {
        "low_stock": state["low_stock"],
        "pending_deliveries": state["pending_deliveries"],
        "monthly_received": state["monthly_received"]
    }

    prompt = f"""
    You are an Inventory Analyst.

    Generate a complete inventory report using the following data:

    {report_data}

    Include these sections:
    1. Low-stock products
    2. Pending deliveries
    3. Inventory received this month

    Use clear headings and bullet points.
    Do not invent or assume missing information.
    """

    response = llm.invoke([
        SystemMessage(content=prompt)
    ])

    return {
        "report": response.content
    }
    
# Build the inventory report workflow

workflow_builder = StateGraph(InventoryReportState)

workflow_builder.add_node("low_stock", low_stock_node)
workflow_builder.add_node("pending_deliveries", pending_deliveries_node)
workflow_builder.add_node("monthly_inventory", monthly_inventory_node)
workflow_builder.add_node("report_generator", report_generator_node)


# Define execution sequence

workflow_builder.add_edge(START, "low_stock")

workflow_builder.add_edge("low_stock", "pending_deliveries")

workflow_builder.add_edge("pending_deliveries", "monthly_inventory")

workflow_builder.add_edge("monthly_inventory", "report_generator")

workflow_builder.add_edge("report_generator", END)


# Compile workflow

inventory_report_workflow = workflow_builder.compile()