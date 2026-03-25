from app.agents.base import BaseAgent
from app.prompts.ux_designer import ux_designer_template
from app.state.schema import AgentState
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class UXDesignerAgent(BaseAgent):
    """UX Designer Agent."""
    
    def get_prompt(self):
        return ux_designer_template
    
    def get_node_name(self) -> str:
        return "ux_designer"
    
    async def process_state(self, state: AgentState) -> Dict[str, Any]:
        """Process the state and return updated output."""
        logger.info("UX Designer creating user experience...")
        
        if not state.get("prd_output"):
            raise ValueError("Missing prd_output")
        
        target_users = state.get("strategist_output", {}).get("target_users", [])
        
        result = await self.process(
            prd_output=json.dumps(state["prd_output"]),
            target_users=json.dumps(target_users)
        )
        
        return {
            "ux_design": result,
            "current_agent": self.get_node_name()
        }

def create_ux_designer_node():
    """Factory function to create UX designer node."""
    agent = UXDesignerAgent()
    
    async def ux_designer_node(state: AgentState) -> AgentState:
        result = await agent.process_state(state)
        return {**state, **result}
    
    return ux_designer_node