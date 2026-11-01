
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from agent.multi_agent_state import MultiAgentState
from agent.supervisor_agent import supervisor_agent
from agent.inventory_agent import inventory_agent_node
from agent.vendor_agent import vendor_agent_node
from agent.analytics_agent import analytics_agent_node
from agent.response_synthesizer import response_synthesizer


def dispatch_agents(state: MultiAgentState):

    selected_agents = state["selected_agents"]

    if not selected_agents:
        return "general"

    return [
        Send(
            agent,
            {
                "messages": state["messages"],
                "next_agent": agent,
                "agent_result": "",
                "selected_agents": [],
                "agent_results": []
            }
        )
        for agent in selected_agents
    ]


def collect_results(state: MultiAgentState):
    return response_synthesizer(state)

def general_response(state: MultiAgentState):
    from langchain_ollama import ChatOllama

    llm = ChatOllama(
        model="qwen3:4b",
        temperature=0
    )

    response = llm.invoke(state["messages"])

    return {
        "agent_result": response.content,
        "messages": [response]
    }

graph_builder = StateGraph(MultiAgentState)

graph_builder.add_node("supervisor", supervisor_agent)

graph_builder.add_node("inventory", inventory_agent_node)
graph_builder.add_node("vendor", vendor_agent_node)
graph_builder.add_node("analytics", analytics_agent_node)

graph_builder.add_node("combine", collect_results)
graph_builder.add_node("general", general_response)

graph_builder.add_edge(START, "supervisor")

graph_builder.add_conditional_edges(
    "supervisor",
    dispatch_agents,
    ["inventory", "vendor", "analytics", "general", END]
)

graph_builder.add_edge("inventory", "combine")
graph_builder.add_edge("vendor", "combine")
graph_builder.add_edge("analytics", "combine")

graph_builder.add_edge("general", END)
graph_builder.add_edge("combine", END)

def create_multi_agent_graph(checkpointer):
    return graph_builder.compile(
        checkpointer=checkpointer
    )
