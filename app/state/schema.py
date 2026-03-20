from typing import TypedDict, Optional, Dict, Any

class AgentState(TypedDict):
    input: str
    strategist_output: Optional[Dict[str, Any]]
    prd_output: Optional[Dict[str, Any]]