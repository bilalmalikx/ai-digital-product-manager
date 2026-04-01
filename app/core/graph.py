"""LangGraph workflow for product generation"""

from langgraph.graph import StateGraph, END
from app.state.schema import AgentState
from app.agents.strategist import create_strategist_node
from app.agents.market_research import create_market_research_node
from app.agents.prd_writer import create_prd_writer_node
from app.agents.tech_architecture import create_tech_architecture_node
from app.agents.ux_design import create_ux_design_node
from app.agents.qa_strategy import create_qa_strategy_node
from app.agents.final_prd_writer import create_final_prd_writer_node  # ✅ ADDED
import logging

logger = logging.getLogger(__name__)


def build_graph() -> StateGraph:
    """
    Build the complete LangGraph workflow for product generation.
    
    Flow:
    Start → Strategist → Market Research → PRD Writer → 
    Tech Architecture → UX Design → QA Strategy → 
    FINAL PRD WRITER → End
    """
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Create all nodes
    strategist_node = create_strategist_node()
    market_research_node = create_market_research_node()
    prd_writer_node = create_prd_writer_node()
    tech_architecture_node = create_tech_architecture_node()
    ux_design_node = create_ux_design_node()
    qa_strategy_node = create_qa_strategy_node()
    final_prd_writer_node = create_final_prd_writer_node()  # ✅ NEW NODE
    
    # Add nodes to graph
    workflow.add_node("strategist_node", strategist_node)
    workflow.add_node("market_research_node", market_research_node)
    workflow.add_node("prd_writer_node", prd_writer_node)
    workflow.add_node("tech_architecture_node", tech_architecture_node)
    workflow.add_node("ux_design_node", ux_design_node)
    workflow.add_node("qa_strategy_node", qa_strategy_node)
    workflow.add_node("final_prd_writer_node", final_prd_writer_node)  # ✅ NEW NODE
    
    # Define edges (flow)
    workflow.set_entry_point("strategist_node")
    
    workflow.add_edge("strategist_node", "market_research_node")
    workflow.add_edge("market_research_node", "prd_writer_node")
    workflow.add_edge("prd_writer_node", "tech_architecture_node")
    workflow.add_edge("tech_architecture_node", "ux_design_node")
    workflow.add_edge("ux_design_node", "qa_strategy_node")
    workflow.add_edge("qa_strategy_node", "final_prd_writer_node")  # ✅ GOES TO FINAL PRD
    workflow.add_edge("final_prd_writer_node", END)  # ✅ THEN END
    
    logger.info("Graph built successfully with Final PRD Writer node")
    
    return workflow.compile()


# For debugging
if __name__ == "__main__":
    graph = build_graph()
    print("Graph structure:")
    print(graph.get_graph().draw_ascii())