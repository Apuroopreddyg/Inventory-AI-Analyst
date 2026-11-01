from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# Step 1: Define State
class AgentState(TypedDict):
    message: str


# Step 2: Create Node 1
def first_node(state: AgentState):
    return {
        "message": state["message"] + " -> First Node executed"
    }


# Step 3: Create Node 2
def second_node(state: AgentState):
    return {
        "message": state["message"] + " -> Second Node executed"
    }


# Step 4: Build Graph
graph_builder = StateGraph(AgentState)

# Step 5: Register Nodes
graph_builder.add_node("first", first_node)
graph_builder.add_node("second", second_node)

# Step 6: Define Flow
graph_builder.add_edge(START, "first")
graph_builder.add_edge("first", "second")
graph_builder.add_edge("second", END)

# Step 7: Compile
graph = graph_builder.compile()

# Step 8: Run
result = graph.invoke({
    "message": "Starting workflow"
})

print(result)