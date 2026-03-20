from services.llm import get_llm
from app.state.schema import AgentState
from app.prompt.get_prd_prompt import prd_template
import json

def prd_node(state: AgentState) -> AgentState:
    llm = get_llm()
    prompt = prd_template.format(
        user_input=state["input"], 
        strategy=state["strategy"]
    )

    response = llm.invoke(prompt)

    try:
        parsed = json.loads(response.content)
    except:
        parsed = {"raw": response.content}

    return {'prd_output': parsed}

