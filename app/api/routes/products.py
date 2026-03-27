from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import (
    ProductCreate, 
    ProductResponse, 
    ProductAPIResponse,
    ProductGenerateRequest,
    ProductGenerateResponse,
    ProductListResponse
)
from typing import List, Optional
from uuid import UUID
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/generate", response_model=ProductGenerateResponse)
async def generate_product(
    request: ProductGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate complete product documentation from idea."""
    
    try:
        service = ProductService(db)
        
        # Run generation
        result = await service.generate_product(
            idea=request.idea,
            product_id=request.product_id
        )
        
        # Return the complete response with all agent outputs
        return ProductGenerateResponse(
            success=True,
            product_id=UUID(result["product_id"]) if result.get("product_id") else None,
            message="Product generated successfully",
            data=result.get("outputs")  # This contains all agent outputs
        )
        
    except Exception as e:
        logger.error(f"Product generation error: {e}")
        return ProductGenerateResponse(
            success=False,
            error=str(e)
        )


@router.get("/{product_id}", response_model=ProductAPIResponse)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """Get product by ID."""
    
    service = ProductService(db)
    product = service.get_product(str(product_id))
    
    if not product:
        return ProductAPIResponse(
            success=False,
            error="Product not found"
        )
    
    return ProductAPIResponse(
        success=True,
        data=product
    )


@router.get("/", response_model=ProductListResponse)
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all products."""
    
    from app.models.product import Product
    
    products = db.query(Product).offset(skip).limit(limit).all()
    total = db.query(Product).count()
    
    return ProductListResponse(
        products=[ProductResponse.model_validate(p) for p in products],
        total=total,
        skip=skip,
        limit=limit
    )