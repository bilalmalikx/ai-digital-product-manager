from langgraph.graph import StateGraph, END
from app.state.schema import AgentState
from app.agents.strategist import strategist_node
from app.agents.prd import prd_node

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("strategist", strategist_node)
    workflow.add_node("prd", prd_node)

    workflow.set_entry_point("strategist")

    workflow.add_edge("strategist", "prd")
    workflow.add_edge("prd", END)

    return workflow.compile()