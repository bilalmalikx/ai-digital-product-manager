from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_core.language_models import BaseChatModel
from app.core.llm import get_llm
import json
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.7):
        self.llm = get_llm(model_name, temperature)
        self.prompt = self.get_prompt()
    
    @abstractmethod
    def get_prompt(self):
        """Return the prompt template for this agent."""
        pass
    
    @abstractmethod
    def get_node_name(self) -> str:
        """Return the node name for the graph."""
        pass
    
    def parse_response(self, response_content: str) -> Dict[str, Any]:
        """Parse LLM response to JSON."""
        try:
            # Try to extract JSON if wrapped in markdown
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0]
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0]
            
            return json.loads(response_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Raw response: {response_content}")
            return {"raw_output": response_content, "error": str(e)}
    
    async def process(self, **kwargs) -> Dict[str, Any]:
        """Process the input and return output."""
        try:
            prompt = self.prompt.format(**kwargs)
            response = await self.llm.ainvoke(prompt)
            parsed_output = self.parse_response(response.content)
            return parsed_output
        except Exception as e:
            logger.error(f"Error in {self.get_node_name()}: {e}")
            return {"error": str(e)}