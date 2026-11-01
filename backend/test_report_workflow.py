from agent.inventory_report_workflow import inventory_report_workflow


initial_state = {
    "low_stock": [],
    "pending_deliveries": [],
    "monthly_received": [],
    "report": ""
}

result = inventory_report_workflow.invoke(initial_state)

print("\n========== INVENTORY REPORT ==========\n")
print(result["report"])