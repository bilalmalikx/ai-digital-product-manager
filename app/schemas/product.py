from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class ProductGenerateRequest(BaseModel):
    idea: str
    product_id: Optional[str] = None

class ProductCreate(BaseModel):
    idea: str
    name: Optional[str] = None
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    final_prd: Optional[str] = None

class ProductResponse(BaseModel):
    """Product data response"""
    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    idea: str
    status: str
    strategist_output: Optional[Dict[str, Any]] = None
    market_research_output: Optional[Dict[str, Any]] = None
    prd_output: Optional[Dict[str, Any]] = None
    tech_architecture: Optional[Dict[str, Any]] = None
    ux_design: Optional[Dict[str, Any]] = None
    qa_strategy: Optional[Dict[str, Any]] = None
    final_prd: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductAPIResponse(BaseModel):
    """Wrapper for API responses"""
    success: bool
    data: Optional[Dict[str, Any]] = None  # Allow dict for flexible response
    message: Optional[str] = None
    error: Optional[str] = None

class ProductGenerateResponse(BaseModel):
    """Response after product generation"""
    success: bool
    product_id: Optional[UUID] = None
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ProductListResponse(BaseModel):
    """List of products response"""
    products: List[ProductResponse]
    total: int
    skip: int
    limit: int

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