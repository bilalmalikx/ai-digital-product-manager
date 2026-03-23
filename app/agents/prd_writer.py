from app.agents.base import BaseAgent
from app.prompts.prd_writer import prd_template
from app.state.schema import AgentState
import json
import logging

logger = logging.getLogger(__name__)

class PRDWriterAgent(BaseAgent):
    """PRD Writer Agent."""
    
    def get_prompt(self):
        return prd_template
    
    def get_node_name(self) -> str:
        return "prd_writer"
    
    async def process_state(self, state: AgentState) -> Dict[str, Any]:
        """Process the state and return updated output."""
        logger.info("PRD Writer creating product requirements...")
        
        if not state.get("strategist_output"):
            raise ValueError("Missing strategist_output")
        
        if not state.get("market_research_output"):
            raise ValueError("Missing market_research_output")
        
        result = await self.process(
            user_input=state["input"],
            strategist_output=json.dumps(state["strategist_output"]),
            market_research=json.dumps(state["market_research_output"])
        )
        
        return {
            "prd_output": result,
            "current_agent": self.get_node_name()
        }

def create_prd_writer_node():
    """Factory function to create PRD writer node."""
    agent = PRDWriterAgent()
    
    async def prd_writer_node(state: AgentState) -> AgentState:
        result = await agent.process_state(state)
        return {**state, **result}
    
    return prd_writer_node