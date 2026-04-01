from langgraph.graph import StateGraph, END
from app.state.schema import AgentState
from app.agents.strategist import create_strategist_node
from app.agents.market_researcher import create_market_researcher_node
from app.agents.prd_writer import create_prd_writer_node
from app.agents.tech_architect import create_tech_architect_node
from app.agents.ux_designer import create_ux_designer_node
from app.agents.qa_engineer import create_qa_engineer_node
from app.agents.final_prd_writer import FinalPRDWriterAgent
import logging

logger = logging.getLogger(__name__)

def build_graph():
    """Build the agent workflow graph."""
    
    # Create nodes
    strategist_node = create_strategist_node()
    market_researcher_node = create_market_researcher_node()
    prd_writer_node = create_prd_writer_node()
    tech_architect_node = create_tech_architect_node()
    ux_designer_node = create_ux_designer_node()
    qa_engineer_node = create_qa_engineer_node()
    final_prd_writer_node = FinalPRDWriterAgent()
    
    # Build workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("market_researcher", market_researcher_node)
    workflow.add_node("prd_writer", prd_writer_node)
    workflow.add_node("tech_architect", tech_architect_node)
    workflow.add_node("ux_designer", ux_designer_node)
    workflow.add_node("qa_engineer", qa_engineer_node)
    workflow.add_node("final_prd_writer", final_prd_writer_node)
    
    # Set entry point
    workflow.set_entry_point("strategist")
    
    # Add edges (sequential workflow)
    workflow.add_edge("strategist", "market_researcher")
    workflow.add_edge("market_researcher", "prd_writer")
    workflow.add_edge("prd_writer", "tech_architect")
    workflow.add_edge("tech_architect", "ux_designer")
    workflow.add_edge("ux_designer", "qa_engineer")
    workflow.add_edge("qa_engineer", "final_prd_writer")
    workflow.add_edge("final_prd_writer", END)
    
    logger.info("Graph built successfully with 7 agents")
    
    return workflow.compile()