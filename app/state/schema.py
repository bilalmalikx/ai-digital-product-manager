from typing import TypedDict, Optional

class AgentState(TypedDict):
    input: str
    strategist_output: Optional[str]
    prd_output: Optional[str]