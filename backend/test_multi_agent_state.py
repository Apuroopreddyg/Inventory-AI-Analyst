
from agent.multi_agent_state import MultiAgentState
from langchain_core.messages import HumanMessage

state: MultiAgentState = {
    "messages": [
        HumanMessage(content="Show low-stock items")
    ],
    "next_agent": "",
    "agent_result": ""
}

print(state)
