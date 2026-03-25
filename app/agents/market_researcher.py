from app.agents.base import BaseAgent
from app.prompts.market_researcher import market_researcher_template
from app.state.schema import AgentState
from app.tools.web_search import web_search_tool
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class MarketResearcherAgent(BaseAgent):
    """Market Research Agent with web search capabilities."""
    
    def get_prompt(self):
        return market_researcher_template
    
    def get_node_name(self) -> str:
        return "market_researcher"
    
    async def process_state(self, state: AgentState) -> Dict[str, Any]:
        """Process the state and return updated output."""
        logger.info("Market Researcher analyzing market data...")
        
        # Perform web search if needed
        search_results = None
        if state.get("strategist_output"):
            try:
                search_query = f"market research {state['strategist_output'].get('market_positioning', '')}"
                search_results = await web_search_tool(search_query)
            except Exception as e:
                logger.error(f"Web search failed: {e}")
        
        result = await self.process(
            idea=state["input"],
            strategist_output=json.dumps(state.get("strategist_output", {})),
            search_results=json.dumps(search_results) if search_results else "No search results"
        )
        
        return {
            "market_research_output": result,
            "current_agent": self.get_node_name()
        }

def create_market_researcher_node():
    """Factory function to create market researcher node."""
    agent = MarketResearcherAgent()
    
    async def market_researcher_node(state: AgentState) -> AgentState:
        result = await agent.process_state(state)
        return {**state, **result}
    
    return market_researcher_node