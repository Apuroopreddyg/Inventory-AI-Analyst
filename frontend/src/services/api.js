
const API_BASE_URL = "http://127.0.0.1:8000";

export async function sendChatMessage(
  question,
  threadId = null,
  mode = "hitl"
) {
  const endpoint =
    mode === "multi-agent" ? "/multi-agent-chat" : "/chat";

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      thread_id: threadId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to communicate with AI.");
  }

  return response.json();
}

export async function submitApproval(threadId, decision) {
  const response = await fetch(`${API_BASE_URL}/approve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      thread_id: threadId,
      decision,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to process approval.");
  }

  return response.json();
}

