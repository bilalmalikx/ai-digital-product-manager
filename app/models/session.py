from sqlalchemy import Column, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel

class Session(BaseModel):
    __tablename__ = "sessions"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    state = Column(JSON, default={})
    current_node = Column(String(100))
    
    product = relationship("Product", back_populates="sessions")