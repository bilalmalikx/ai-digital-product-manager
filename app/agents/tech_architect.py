from app.agents.base import BaseAgent
from app.prompts.tech_architect import tech_architect_template
from typing import Dict, Any
from app.state.schema import AgentState
import json
import logging

logger = logging.getLogger(__name__)

class TechArchitectAgent(BaseAgent):
    """Technical Architect Agent."""
    
    def get_prompt(self):
        return tech_architect_template
    
    def get_node_name(self) -> str:
        return "tech_architect"
    
    async def process_state(self, state: AgentState) -> Dict[str, Any]:
        """Process the state and return updated output."""
        logger.info("Tech Architect designing system architecture...")
        
        if not state.get("prd_output"):
            raise ValueError("Missing prd_output")
        
        result = await self.process(
            prd_output=json.dumps(state["prd_output"]),
            strategist_output=json.dumps(state.get("strategist_output", {}))
        )
        
        return {
            "tech_architecture": result,
            "current_agent": self.get_node_name()
        }

def create_tech_architect_node():
    """Factory function to create tech architect node."""
    agent = TechArchitectAgent()
    
    async def tech_architect_node(state: AgentState) -> AgentState:
        result = await agent.process_state(state)
        return {**state, **result}
    
    return tech_architect_node