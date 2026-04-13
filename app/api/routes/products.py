"""Updated API with multi-format input support"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.product_service import ProductService
from app.services.input_processor import InputProcessor
from app.guardrails.input_guardrail import validate_product_idea
from app.guardrails.output_guardrail import filter_agent_output
from app.schemas.product import (
    ProductCreate, 
    ProductResponse, 
    ProductAPIResponse,
    ProductGenerateRequest,
    ProductGenerateResponse,
    ProductListResponse,
    MultiFormatInputRequest
)
from typing import List, Optional
from uuid import UUID
import logging
import json
import asyncio
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/generate", response_model=ProductGenerateResponse)
async def generate_product(
    request: ProductGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        validate_product_idea(request.idea)

        service = ProductService(db)

        result = await service.generate_product(
            idea=request.idea,
            product_id=request.product_id
        )

        clean_output = filter_agent_output(result.get("outputs", {}))

        return ProductGenerateResponse(
            success=True,
            product_id=UUID(result["product_id"]) if result.get("product_id") else None,
            message="Product generated successfully",
            data=clean_output
        )

    except Exception as e:
        logger.error(f"Product generation error: {e}")
        return ProductGenerateResponse(
            success=False,
            error=str(e)
        )


@router.post("/generate-from-files")
async def generate_product_from_files(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    idea: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    urls: Optional[str] = Form(None)  # Comma-separated URLs
):
    """
    Generate product from multiple file formats and URLs.
    
    Supports:
    - PDF, Word, Excel, Text, Markdown files
    - Audio/Video files (transcription)
    - URLs (web pages, Google Docs)
    - Direct text input
    """
    
    try:
        processor = InputProcessor()
        inputs = []
        
        # Add direct text if provided
        if idea:
            inputs.append({"type": "text", "content": idea})
        
        # Process uploaded files
        for file in files:
            # Save temporarily
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            inputs.append({"type": "file", "path": temp_path})
        
        # Process URLs
        if urls:
            for url in urls.split(","):
                url = url.strip()
                if url:
                    inputs.append({"type": "url", "url": url})
        
        # Process all inputs
        processed = await processor.process_inputs(inputs)
        
        # Clean up temp files
        for inp in inputs:
            if inp.get("type") == "file" and "path" in inp:
                try:
                    os.remove(inp["path"])
                except:
                    pass
        
        # Now generate product using the consolidated idea
        service = ProductService(db)
        result = await service.generate_product(
            idea=processed["consolidated_idea"],
            product_id=None
        )
        
        return {
            "success": True,
            "product_id": result["product_id"],
            "input_summary": {
                "sources_processed": processed["source_count"],
                "consolidated_idea": processed["consolidated_idea"],
                "requirements_found": len(processed.get("requirements", [])),
                "constraints_found": len(processed.get("constraints", []))
            },
            "outputs": result["outputs"]
        }
        
    except Exception as e:
        logger.error(f"Multi-format generation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/generate-stream")
async def generate_product_stream(
    request: ProductGenerateRequest,
    db: Session = Depends(get_db)
):
    """Streaming generation with word-by-word output"""
    
    service = ProductService(db)
    
    async def event_generator():
        async for event in service.generate_product_stream(
            idea=request.idea,
            product_id=request.product_id
        ):
            clean_event = filter_agent_output(event)
            yield f"data: {json.dumps(clean_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/generate-from-files-stream")
async def generate_from_files_stream(
    db: Session = Depends(get_db),
    idea: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    urls: Optional[str] = Form(None)
):
    """Streaming generation from multiple file formats"""
    
    async def event_generator():
        try:
            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'message': 'Processing inputs...'})}\n\n"
            
            processor = InputProcessor()
            inputs = []
            
            # Process direct text
            if idea:
                inputs.append({"type": "text", "content": idea})
                yield f"data: {json.dumps({'type': 'progress', 'message': '✓ Text input added'})}\n\n"
            
            # Process files
            for file in files:
                temp_path = f"/tmp/{file.filename}"
                with open(temp_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                inputs.append({"type": "file", "path": temp_path})
                yield f"data: {json.dumps({'type': 'progress', 'message': f'✓ File added: {file.filename}'})}\n\n"
            
            # Process URLs
            if urls:
                url_list = [u.strip() for u in urls.split(",") if u.strip()]
                for url in url_list:
                    inputs.append({"type": "url", "url": url})
                    yield f"data: {json.dumps({'type': 'progress', 'message': f'✓ URL added: {url}'})}\n\n"
            
            # Process all inputs
            yield f"data: {json.dumps({'type': 'progress', 'message': 'Consolidating requirements from all sources...'})}\n\n"
            
            processed = await processor.process_inputs(inputs)
            
            # FIXED: Use double quotes for outer f-string, single quotes for inner dict keys
            source_count = processed["source_count"]
            consolidated_idea = processed["consolidated_idea"][:100]
            
            yield f"data: {json.dumps({'type': 'progress', 'message': f'✓ Processed {source_count} sources'})}\n\n"
            yield f"data: {json.dumps({'type': 'progress', 'message': f'✓ Idea extracted: {consolidated_idea}...'})}\n\n"
            
            # Clean up temp files
            for inp in inputs:
                if inp.get("type") == "file" and "path" in inp:
                    try:
                        os.remove(inp["path"])
                    except:
                        pass
            
            # Generate product with streaming
            service = ProductService(db)
            async for event in service.generate_product_stream(
                idea=processed["consolidated_idea"],
                product_id=None
            ):
                yield f"data: {json.dumps(event)}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
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