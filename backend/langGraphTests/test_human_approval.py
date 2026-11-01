
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command


# 1. Define the graph state
class ApprovalState(TypedDict):
    action: str
    approved: bool
    message: str


# 2. Create the approval node
def approval_node(state: ApprovalState):

    # Pause execution and request human approval
    decision = interrupt({
        "question": "Do you approve this inventory action?",
        "action": state["action"],
        "options": ["approve", "reject"]
    })

    # This code executes only after the graph resumes
    return {
        "approved": decision == "approve"
    }


# 3. Create the execution node
def execute_node(state: ApprovalState):

    if state["approved"]:
        return {
            "message": f"Action approved and executed: {state['action']}"
        }

    return {
        "message": f"Action rejected. Nothing executed: {state['action']}"
    }


# 4. Build the graph
graph_builder = StateGraph(ApprovalState)

graph_builder.add_node("approval", approval_node)
graph_builder.add_node("execute", execute_node)

graph_builder.add_edge(START, "approval")
graph_builder.add_edge("approval", "execute")
graph_builder.add_edge("execute", END)


# 5. Compile with SQLite checkpointer
with SqliteSaver.from_conn_string("checkpoints.sqlite") as checkpointer:

    graph = graph_builder.compile(checkpointer=checkpointer)

    # 6. Unique ID for this workflow
    config = {
        "configurable": {
            "thread_id": "inventory-approval-test-001"
        }
    }

    # 7. Start execution
    result = graph.invoke(
        {
            "action": "Reorder 100 Router units",
            "approved": False,
            "message": ""
        },
        config=config
    )

    # 8. Check whether execution was interrupted
    if "__interrupt__" in result:

        print("\n--- HUMAN APPROVAL REQUIRED ---")

        for interruption in result["__interrupt__"]:
            print(interruption.value)

        # 9. Simulate human approval
        decision = input("\nEnter approval decision (approve/reject): ").strip().lower()

        # 10. Resume the SAME graph using the SAME thread_id
        result = graph.invoke(
            Command(resume=decision),
            config=config
        )

    print("\n--- FINAL RESULT ---")
    print(result)
