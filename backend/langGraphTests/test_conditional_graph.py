from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# Step 1: Define State
class AgentState(TypedDict):
    number: int
    result: str


# Step 2: Create Node
def check_number(state: AgentState):
    if state["number"] > 0:
        return {"result": "The number is positive"}

    return {"result": "The number is zero or negative"}


# Step 3: Define Routing Function
def route_number(state: AgentState):
    if state["number"] > 0:
        return "positive"

    return "non_positive"


# Step 4: Create Nodes
def positive_node(state: AgentState):
    return {"result": state["result"] + " -> Positive path"}

def non_positive_node(state: AgentState):
    return {"result": state["result"] + " -> Non-positive path"}


# Step 5: Build Graph
graph_builder = StateGraph(AgentState)

graph_builder.add_node("check", check_number)
graph_builder.add_node("positive", positive_node)
graph_builder.add_node("non_positive", non_positive_node)

# Step 6: Define Edges
graph_builder.add_edge(START, "check")

graph_builder.add_conditional_edges(
    "check",
    route_number,
    {
        "positive": "positive",
        "non_positive": "non_positive"
    }
)

graph_builder.add_edge("positive", END)
graph_builder.add_edge("non_positive", END)

# Step 7: Compile
graph = graph_builder.compile()


# Step 8: Test
result = graph.invoke({
    "number": -5,
    "result": ""
})

print(result)