from app.services.llm import get_llm
from app.state.schema import AgentState
from app.prompts.prd import prd_template
import json

llm = get_llm()

def prd_node(state: AgentState) -> AgentState:

    if not state.get("strategist_output"):
        raise ValueError("Missing strategist_output in state")

    prompt = prd_template.format(
        user_input=state["input"],
        strategist_output=state["strategist_output"]
    )

    response = llm.invoke(prompt)

    try:
        parsed = json.loads(response.content)
    except Exception:
        parsed = {"raw": response.content}

    return {
        "prd_output": parsed
    }