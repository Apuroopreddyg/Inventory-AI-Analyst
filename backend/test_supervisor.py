
from agent.supervisor_agent import supervisor_agent
from agent.multi_agent_state import MultiAgentState
from langchain_core.messages import HumanMessage

questions = [
    "Show low-stock items",
    "Which vendors have pending deliveries?",
    "Generate a complete inventory report",
    "Hello, how are you?"
]

for question in questions:

    state: MultiAgentState = {
        "messages": [HumanMessage(content=question)],
        "next_agent": "",
        "agent_result": ""
    }

    result = supervisor_agent(state)

    print(f"\nQuestion: {question}")
    print(f"Decision: {result['next_agent']}")
