from pydantic import BaseModel
from typing import Literal


class ChatRequest(BaseModel):
    question: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    thread_id: str
    status: str
    response: str | None = None
    approval_required: bool = False
    approval_details: dict | None = None


class ApprovalRequest(BaseModel):
    thread_id: str
    decision: Literal["approve", "reject"]