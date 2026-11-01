
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from langchain.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from uuid import uuid4
from agent.inventory_hitl_graph import create_inventory_hitl_graph
from schemas.api_schema import (
    ChatRequest,
    ChatResponse,
    ApprovalRequest,
)


# --------------------------------
# Checkpointer and graph lifecycle
# --------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] Initializing Inventory AI Analyst...")

    with SqliteSaver.from_conn_string("inventory_api.sqlite") as checkpointer:
        app.state.inventory_graph = create_inventory_hitl_graph(
            checkpointer
        )

        print("[STARTUP] LangGraph initialized successfully.")
        print("[STARTUP] SQLite checkpointer connected.")

        yield

    print("[SHUTDOWN] Inventory AI Analyst shutting down.")


app = FastAPI(
    title="Inventory AI Analyst",
    description="AI-powered inventory management assistant using LangGraph.",
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------
# POST /chat
# --------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Generate a new thread ID if the client didn't provide one
    thread_id = request.thread_id or str(uuid4())
    
    print("\n[CHAT] New chat request received.")
    print(f"[CHAT] Thread ID: {thread_id}")
    print(f"[CHAT] User question: {request.question}")

    graph = app.state.inventory_graph

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "messages": [
            HumanMessage(content=request.question)
        ],
        "pending_action": {},
        "approval_status": ""
    }

    try:
        print("[CHAT] Invoking LangGraph workflow...")
        result = graph.invoke(
            initial_state,
            config=config
        )

        print("[CHAT] LangGraph execution completed.")

        # Check whether the graph paused for HITL approval
        if "__interrupt__" in result:

            interruption = result["__interrupt__"][0]

            print("[HITL] Human approval required.")
            print(f"[HITL] Approval details: {interruption.value}")

            return ChatResponse(
                thread_id=thread_id,
                status="pending_approval",
                approval_required=True,
                approval_details=interruption.value
            )

        # Normal response from the graph
        last_message = result["messages"][-1]

        print("[CHAT] Response generated successfully.")
        print(f"[CHAT] Agent response: {last_message.content}")

        return ChatResponse(
            thread_id=thread_id,
            status="completed",
            response=last_message.content
        )

    except Exception as e:
        print(f"[ERROR] Chat execution failed: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Inventory agent error: {str(e)}"
        )


# --------------------------------
# POST /approve
# --------------------------------

@app.post("/approve", response_model=ChatResponse)
def approve_action(request: ApprovalRequest):

    print("\n[APPROVAL] Approval request received.")
    print(f"[APPROVAL] Thread ID: {request.thread_id}")
    print(f"[APPROVAL] Human decision: {request.decision}")

    graph = app.state.inventory_graph

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    try:
        print("[APPROVAL] Resuming interrupted LangGraph workflow...")

        result = graph.invoke(
            Command(resume=request.decision),
            config=config
        )

        print("[APPROVAL] LangGraph execution resumed.")

        # Check if another interruption occurred
        if "__interrupt__" in result:

            interruption = result["__interrupt__"][0]

            print("[HITL] Another approval is required.")
            print(f"[HITL] Approval details: {interruption.value}")

            return ChatResponse(
                thread_id=request.thread_id,
                status="pending_approval",
                approval_required=True,
                approval_details=interruption.value
            )

        # Retrieve the execution/rejection result
        last_message = result["messages"][-1]

        print("[APPROVAL] Workflow completed successfully.")
        print(f"[APPROVAL] Final result: {last_message.content}")

        return ChatResponse(
            thread_id=request.thread_id,
            status="completed",
            response=last_message.content,
            approval_required=False
        )

    except Exception as e:
        print(f"[ERROR] Approval processing failed: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Approval processing error: {str(e)}"
        )
