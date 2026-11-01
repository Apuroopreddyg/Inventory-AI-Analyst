
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from agent.multi_agent_state import MultiAgentState


llm = ChatOllama(
    model="qwen3:4b",
    temperature=0
)

SYNTHESIZER_PROMPT = """
You are the Final Response Generator for an Inventory AI Analyst.

You receive responses from multiple specialist agents.

Your responsibilities:
1. Combine their findings into one coherent response.
2. Remove redundant information and contradictory disclaimers.
3. Preserve all relevant facts, numbers, product names, and vendors.
4. Organize the response using headings and bullet points when useful.
5. Do not invent information or conclusions.
6. If a specialist did not provide information, do not fabricate it.
7. Return only the final answer intended for the user.
IMPORTANT:
- Do not include tool limitations or specialist capability disclaimers.
- Specialists are intentionally focused on different domains.
- Combine their factual findings directly.
- Never interpret one specialist's lack of information as a system limitation.
"""


def response_synthesizer(state: MultiAgentState):

    results = state.get("agent_results", [])

    specialist_responses = "\n\n".join(
        f"{agent.upper()} SPECIALIST:\n{result}"
        for item in results
        for agent, result in item.items()
    )

    response = llm.invoke([
        SystemMessage(content=SYNTHESIZER_PROMPT),
        HumanMessage(
            content=f"Combine these specialist responses:\n\n{specialist_responses}"
        )
    ])

    final_answer = response.content

    return {
        "messages": [response],
        "agent_result": final_answer
    }
