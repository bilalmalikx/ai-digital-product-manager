from app.agents.base import BaseAgent
from app.prompts.strategist import strategist_template
from app.state.schema import AgentState
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class StrategistAgent(BaseAgent):
    """Product Strategist Agent."""
    
    def get_prompt(self):
        return strategist_template
    
    def get_node_name(self) -> str:
        return "strategist"
    
    async def process_state(self, state: AgentState) -> Dict[str, Any]:
        """Process the state and return updated output."""
        logger.info(f"Strategist processing idea: {state['input'][:100]}...")
        
        result = await self.process(idea=state["input"])
        
        return {
            "strategist_output": result,
            "current_agent": self.get_node_name()
        }

def create_strategist_node():
    """Factory function to create strategist node."""
    agent = StrategistAgent()
    
    async def strategist_node(state: AgentState) -> AgentState:
        result = await agent.process_state(state)
        return {**state, **result}
    
    return strategist_node