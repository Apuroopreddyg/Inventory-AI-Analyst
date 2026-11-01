
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from operator import add


class MultiAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str
    agent_result: str
    selected_agents: list[str]

    inventory_result: str
    vendor_result: str
    analytics_result: str

    agent_results: Annotated[list, add]
