"""Final PRD Writer Agent - Sab state collect karke final PRD generate karta hai"""

from app.agents.base import BaseAgent
from app.prompts.final_prd import final_prd_template
from app.state.schema import AgentState
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class FinalPRDWriterAgent(BaseAgent):
    """
    Final PRD Writer Agent
    
    Ye agent saare previous agents ke outputs collect karta hai
    aur ek final, cohesive PRD generate karta hai.
    """
    
    def get_prompt(self):
        return final_prd_template
    
    def get_node_name(self) -> str:
        return "final_prd_writer"
    
    async def process_state(self, state: AgentState) -> Dict[str, Any]:
        """
        Process all collected state and generate final PRD
        """
        logger.info("Final PRD Writer: Generating comprehensive PRD...")
        
        # Validate required outputs
        required_fields = [
            "strategist_output", 
            "market_research_output", 
            "prd_output",
            "tech_architecture",
            "ux_design",
            "qa_strategy"
        ]
        
        missing_fields = [f for f in required_fields if not state.get(f)]
        if missing_fields:
            raise ValueError(f"Missing required outputs: {missing_fields}")
        
        # Sab outputs ko collect karo
        all_inputs = {
            "user_input": state.get("input"),
            "strategist_output": json.dumps(state.get("strategist_output"), indent=2),
            "market_research": json.dumps(state.get("market_research_output"), indent=2),
            "prd_draft": json.dumps(state.get("prd_output"), indent=2),
            "tech_architecture": json.dumps(state.get("tech_architecture"), indent=2),
            "ux_design": json.dumps(state.get("ux_design"), indent=2),
            "qa_strategy": json.dumps(state.get("qa_strategy"), indent=2)
        }
        
        # Generate final PRD
        result = await self.process(**all_inputs)
        
        # Parse result if it's JSON string
        try:
            parsed_result = json.loads(result) if isinstance(result, str) else result
        except json.JSONDecodeError:
            parsed_result = {"final_prd_text": result}
        
        return {
            "final_prd": parsed_result,
            "current_agent": self.get_node_name(),
            "status": "prd_generated"
        }


def create_final_prd_writer_node():
    """Factory function to create final PRD writer node."""
    agent = FinalPRDWriterAgent()
    
    async def final_prd_writer_node(state: AgentState) -> AgentState:
        result = await agent.process_state(state)
        return {**state, **result}
    
    return final_prd_writer_node