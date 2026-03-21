from typing import TypedDict, Optional, Dict, Any
from pydantic import BaseModel

class AgentState(TypedDict):
    input: str
    strategist_output: Optional[Dict[str, Any]]
    prd_output: Optional[Dict[str, Any]]

class ProductVision(BaseModel):
    target_users: List[str]
    problem_statement: str
    value_proposition: str

class MarketResearch(BaseModel):
    competitors: List[str]
    trends: List[str]
    opportunities: List[str]

class FeatureItem(BaseModel):
    name: str
    description: str
    priority: str 

class RoadmapItem(BaseModel):
    phase: str
    features: List[str]

class AgentState(BaseModel):
    idea: str

    product_vision: Optional[ProductVision] = None
    market_research: Optional[MarketResearch] = None
    features: Optional[List[FeatureItem]] = None
    roadmap: Optional[List[RoadmapItem]] = None
    prd: Optional[str] = None
    tech_architecture: Optional[str] = None