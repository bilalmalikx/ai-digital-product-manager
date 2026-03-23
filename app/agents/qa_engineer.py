from app.agents.base import BaseAgent
from app.prompts.qa_engineer import qa_engineer_template
from app.state.schema import AgentState
import json
import logging

logger = logging.getLogger(__name__)

class QAEngineerAgent(BaseAgent):
    """QA Engineer Agent."""
    
    def get_prompt(self):
        return qa_engineer_template
    
    def get_node_name(self) -> str:
        return "qa_engineer"
    
    async def process_state(self, state: AgentState) -> Dict[str, Any]:
        """Process the state and return updated output."""
        logger.info("QA Engineer creating testing strategy...")
        
        if not state.get("prd_output"):
            raise ValueError("Missing prd_output")
        
        result = await self.process(
            prd_output=json.dumps(state["prd_output"]),
            tech_architecture=json.dumps(state.get("tech_architecture", {}))
        )
        
        return {
            "qa_strategy": result,
            "current_agent": self.get_node_name()
        }

def create_qa_engineer_node():
    """Factory function to create QA engineer node."""
    agent = QAEngineerAgent()
    
    async def qa_engineer_node(state: AgentState) -> AgentState:
        result = await agent.process_state(state)
        return {**state, **result}
    
    return qa_engineer_node