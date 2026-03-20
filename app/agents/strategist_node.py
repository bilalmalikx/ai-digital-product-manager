from app.services.llm import get_llm
from app.prompt.get_strategist_prompt import strategist_template
from app.state.schema import AgentState

def strategist_node(state: AgentState) -> AgentState:
    llm = get_llm()
    prompt = strategist_template.format(idea=state["input"])
    response = llm.invoke(prompt)
    return {'strategist_output': response.content}