
from langchain_ollama import ChatOllama

from agent.multi_agent_state import MultiAgentState


llm = ChatOllama(
    model="qwen3:4b",
    temperature=0
)

SUPERVISOR_PROMPT = """
You are a Supervisor Agent for an Inventory AI Analyst.

Your task is to select specialist agents to handle the user's query.

Available specialists:

1. inventory
   Handles current stock, low-stock items, inventory quantities,
   and inventory received this month.

2. vendor
   Handles vendors, suppliers, pending deliveries,
   and vendor-related questions.

3. analytics
   Handles complete inventory reports, summaries, and trends.

Rules:
- Select ALL specialists required to answer the query.
- Select multiple specialists when the query requires multiple domains.
- Select only one specialist when sufficient.
- For general conversation, respond with FINISH.
- Do NOT answer the user's question yourself.

Return ONLY a comma-separated list of specialist names.
Valid names: inventory, vendor, analytics
For general conversation: FINISH

Examples:
"Show low-stock items" → inventory
"Which vendors have pending deliveries?" → vendor
"Show low-stock items and pending deliveries" → inventory, vendor
"Generate a complete inventory report" → analytics
"Hello" → FINISH
"""


def supervisor_agent(state: MultiAgentState):

    response = llm.invoke([
        ("system", SUPERVISOR_PROMPT),
        *state["messages"]
    ])

    decision = response.content.strip().lower()

    if "finish" in decision:
        selected_agents = []
    else:
        selected_agents = [
            agent.strip()
            for agent in decision.split(",")
            if agent.strip() in ["inventory", "vendor", "analytics"]
        ]

    print(f"[SUPERVISOR] Selected: {selected_agents}")

    return {
        "selected_agents": selected_agents,
        "next_agent": (
            selected_agents[0]
            if selected_agents
            else "FINISH"
        )
    }
