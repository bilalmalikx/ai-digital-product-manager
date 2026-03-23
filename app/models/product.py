from sqlalchemy import Column, String, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import enum

class ProductStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class Product(BaseModel):
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    idea = Column(Text, nullable=False)
    status = Column(Enum(ProductStatus), default=ProductStatus.DRAFT)
    
    # Agent outputs
    strategist_output = Column(JSON)
    market_research_output = Column(JSON)
    prd_output = Column(JSON)
    tech_architecture = Column(JSON)
    ux_design = Column(JSON)
    qa_strategy = Column(JSON)
    
    # Final PRD
    final_prd = Column(Text)
    
    # Relationships
    sessions = relationship("Session", back_populates="product")