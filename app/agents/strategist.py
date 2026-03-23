from app.services.llm import get_llm
from app.prompt.get_strategist_prompt import strategist_template
from app.state.schema import AgentState
import json

llm = get_llm()

def strategist_node(state: AgentState) -> AgentState:
    prompt = strategist_template.format(idea=state["input"])
    response = llm.invoke(prompt)

    try:
        parsed = json.loads(response.content)
    except Exception:
        parsed = {"raw": response.content}

    return {
        "strategist_output": parsed
    }