from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductResponse, ProductGenerateRequest
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/generate", response_model=ProductResponse)
async def generate_product(
    request: ProductGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate complete product documentation from idea."""
    
    try:
        service = ProductService(db)
        
        # Run in background for long-running tasks
        result = await service.generate_product(
            idea=request.idea,
            product_id=request.product_id
        )
        
        return ProductResponse(
            success=True,
            data=result,
            message="Product generation started successfully"
        )
        
    except Exception as e:
        logger.error(f"Product generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get product by ID."""
    
    service = ProductService(db)
    product = service.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse(
        success=True,
        data=product
    )

@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all products."""
    
    from app.models.product import Product
    
    products = db.query(Product).offset(skip).limit(limit).all()
    
    return [
        ProductResponse(
            success=True,
            data={
                "id": str(p.id),
                "name": p.name,
                "idea": p.idea,
                "status": p.status,
                "created_at": p.created_at
            }
        )
        for p in products
    ]