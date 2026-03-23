from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ProductGenerateRequest(BaseModel):
    idea: str
    product_id: Optional[str] = None

class ProductCreate(BaseModel):
    idea: str
    name: Optional[str] = None

class ProductResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None