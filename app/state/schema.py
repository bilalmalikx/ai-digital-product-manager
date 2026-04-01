from typing import TypedDict, Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

class StrategistOutput(BaseModel):
    market_positioning: str
    target_users: List[str]
    strategy: str
    competitive_advantage: str

class MarketResearchOutput(BaseModel):
    competitors: List[Dict[str, str]]
    market_size: str
    trends: List[str]
    opportunities: List[str]
    threats: List[str]

class PRDOutput(BaseModel):
    features: List[Dict[str, Any]]
    requirements: List[str]
    user_stories: List[str]
    success_metrics: List[str]

class TechArchitecture(BaseModel):
    tech_stack: Dict[str, List[str]]
    system_design: str
    api_endpoints: List[str]
    database_schema: List[Dict[str, Any]]
    security_considerations: List[str]

class UXDesign(BaseModel):
    user_flows: List[Dict[str, Any]]
    wireframes: List[str]
    design_system: Dict[str, Any]
    accessibility: List[str]

class QAStrategy(BaseModel):
    test_cases: List[Dict[str, Any]]
    testing_approach: str
    automation_strategy: str
    performance_benchmarks: List[str]

class AgentState(TypedDict):
    # Input
    input: str
    product_id: Optional[str]
    
    # Agent outputs
    strategist_output: Optional[Dict[str, Any]]
    market_research_output: Optional[Dict[str, Any]]
    prd_output: Optional[Dict[str, Any]]
    tech_architecture: Optional[Dict[str, Any]]
    ux_design: Optional[Dict[str, Any]]
    qa_strategy: Optional[Dict[str, Any]]

    final_prd: Optional[str]
    functions_list: Optional[List[Dict]]
    
    # Metadata
    current_agent: Optional[str]
    errors: Optional[List[str]]
    timestamp: Optional[str]

# Add these to your existing schemas

class MultiFormatInputRequest(BaseModel):
    """Multi-format input request"""
    idea: Optional[str] = None
    file_paths: Optional[List[str]] = None  # Local file paths
    urls: Optional[List[str]] = None
    audio_paths: Optional[List[str]] = None
    video_paths: Optional[List[str]] = None

class ProcessedInputResponse(BaseModel):
    """Response after processing multiple inputs"""
    success: bool
    consolidated_idea: str
    requirements: List[str]
    constraints: List[str]
    stakeholders: List[str]
    open_questions: List[str]
    sources_processed: int
    errors: Optional[List[str]] = None