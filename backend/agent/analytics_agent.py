
from agent.multi_agent_state import MultiAgentState
from tools.inventory_tools import generate_inventory_report


def analytics_agent_node(state: MultiAgentState):

    # Execute the existing inventory report workflow
    result = generate_inventory_report.invoke({})

    from langchain_core.messages import AIMessage

    response = AIMessage(content=result)

    return {
        "messages": [response],
        "analytics_result": result,
        "agent_results": [
            {"analytics": result}
        ],
    }
