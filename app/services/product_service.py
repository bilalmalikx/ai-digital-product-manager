# app/services/product_service.py
from sqlalchemy.orm import Session
from app.models.product import Product, ProductStatus
from app.models.session import Session as SessionModel
from app.core.graph import build_graph
from app.tools.database_tools import DatabaseTools
from app.tools.mcp_tools import mcp_tools
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID

logger = logging.getLogger(__name__)

class ProductService:
    """Service for managing product generation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.db_tools = DatabaseTools(db)
        self.graph = build_graph()
    
    async def generate_product(self, idea: str, product_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate complete product documentation."""
        
        try:
            # Save initial product
            product = self.db_tools.save_product({
                "id": product_id,
                "idea": idea,
                "name": idea[:100]  # Temporary name
            })
            
            # Prepare initial state
            initial_state = {
                "input": idea,
                "product_id": str(product.id),
                "strategist_output": None,
                "market_research_output": None,
                "prd_output": None,
                "tech_architecture": None,
                "ux_design": None,
                "qa_strategy": None,
                "final_prd": None,
                "current_agent": "start",
                "errors": [],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Update product with all outputs
            product.strategist_output = final_state.get("strategist_output")
            product.market_research_output = final_state.get("market_research_output")
            product.prd_output = final_state.get("prd_output")
            product.tech_architecture = final_state.get("tech_architecture")
            product.ux_design = final_state.get("ux_design")
            product.qa_strategy = final_state.get("qa_strategy")
            product.final_prd = final_state.get("final_prd")
            product.status = ProductStatus.IN_REVIEW
            
            # Generate final PRD document using MCP
            final_prd = await mcp_tools.generate_prd_document({
                "product": {
                    "name": product.name,
                    "idea": product.idea,
                    "strategist": product.strategist_output,
                    "market_research": product.market_research_output,
                    "prd": product.prd_output,
                    "tech_architecture": product.tech_architecture,
                    "ux_design": product.ux_design,
                    "qa_strategy": product.qa_strategy,
                    "final_prd": product.final_prd
                }
            })
            
            if final_prd:
                product.final_prd = final_prd
            
            # Save session
            self.db_tools.save_session_state(
                str(product.id),
                final_state,
                final_state.get("current_agent", "completed")
            )
            
            self.db.commit()
            self.db.refresh(product)
            
            # Return all outputs in a structured format
            return {
                "product_id": str(product.id),
                "status": product.status.value if hasattr(product.status, 'value') else product.status,
                "outputs": {
                    "strategist": product.strategist_output,
                    "market_research": product.market_research_output,
                    "prd": product.prd_output,
                    "tech_architecture": product.tech_architecture,
                    "ux_design": product.ux_design,
                    "qa_strategy": product.qa_strategy,
                    "final_prd": product.final_prd
                }
            }
            
        except Exception as e:
            logger.error(f"Product generation failed: {e}")
            self.db.rollback()
            raise
    
    async def generate_product_stream(self, idea: str, product_id: Optional[str] = None):
        """Generate product with streaming updates - word by word"""
        
        try:
            # Save initial product
            product = self.db_tools.save_product({
                "id": product_id,
                "idea": idea,
                "name": idea[:100]
            })
            
            yield {
                "type": "product_created",
                "product_id": str(product.id),
                "message": f"📦 Product created: {product.id}"
            }
            
            # Prepare initial state
            initial_state = {
                "input": idea,
                "product_id": str(product.id),
                "strategist_output": None,
                "market_research_output": None,
                "prd_output": None,
                "tech_architecture": None,
                "ux_design": None,
                "qa_strategy": None,
                "final_prd": None,
                "current_agent": "start",
                "errors": [],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Define agents in order
            agents = [
                ("strategist_node", "strategist_output", "📊 Strategist analyzing market..."),
                ("market_research_node", "market_research_output", "🔍 Conducting market research..."),
                ("prd_node", "prd_output", "📋 Generating PRD..."),
                ("tech_architecture_node", "tech_architecture", "🏗️ Designing tech architecture..."),
                ("ux_design_node", "ux_design", "🎨 Creating UX design..."),
                ("qa_strategy_node", "qa_strategy", "🧪 Developing QA strategy..."),
                ("final_prd_writer_node", "final_prd", "📝 Generating final PRD...")
            ]
            
            current_state = initial_state
            all_outputs = {}
            
            for agent_name, output_key, message in agents:
                # Send start event
                yield {
                    "type": "agent_start",
                    "agent": agent_name,
                    "message": message
                }
                
                # Simulate agent work
                await asyncio.sleep(1.5)
                
                # Mock output
                mock_output = {
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "analysis": f"Detailed analysis from {agent_name}",
                    "recommendations": [
                        "Recommendation 1",
                        "Recommendation 2",
                        "Recommendation 3"
                    ]
                }
                
                # Update state and product
                current_state[output_key] = mock_output
                all_outputs[output_key] = mock_output
                
                # Update product in database
                if agent_name == "strategist_node":
                    product.strategist_output = mock_output
                elif agent_name == "market_research_node":
                    product.market_research_output = mock_output
                elif agent_name == "prd_node":
                    product.prd_output = mock_output
                elif agent_name == "tech_architecture_node":
                    product.tech_architecture = mock_output
                elif agent_name == "ux_design_node":
                    product.ux_design = mock_output
                elif agent_name == "qa_strategy_node":
                    product.qa_strategy = mock_output
                elif agent_name == "final_prd_writer_node":
                    product.final_prd = mock_output
                
                self.db.commit()
                
                # Send complete event
                yield {
                    "type": "agent_complete",
                    "agent": agent_name,
                    "output": mock_output,
                    "message": f"✅ {message.replace('...', ' complete!')}"
                }
                
                # Send outputs update
                yield {
                    "type": "outputs_update",
                    "outputs": all_outputs.copy()
                }
            
            # Generate final PRD
            yield {
                "type": "generating_final",
                "message": "📝 Generating final PRD document..."
            }
            
            prd_content = f"""
# Product Requirements Document

## Product Name: {product.name}

## Idea: {product.idea}

## Executive Summary
This comprehensive PRD outlines the complete product specifications for {product.name}, an innovative solution built with modern technologies.

## Market Analysis
Based on our market research, this product addresses key gaps in the current market landscape.

## Technical Architecture
The system will be built using:
- **Frontend**: Angular 17+ with standalone components
- **Backend**: FastAPI with async support
- **Database**: PostgreSQL with Redis caching
- **Deployment**: Docker containers on Kubernetes

## Features
1. **User Authentication**: Secure JWT-based authentication
2. **Real-time Updates**: WebSocket connections for live data
3. **Scalable Architecture**: Horizontal scaling support
4. **Analytics Dashboard**: Comprehensive metrics and insights

## Timeline
- **Phase 1 (2 weeks)**: Core setup and authentication
- **Phase 2 (3 weeks)**: Main features implementation
- **Phase 3 (2 weeks)**: Testing and deployment

## Success Metrics
- User adoption rate > 70%
- Response time < 200ms
- 99.9% uptime
"""
            
            # Stream word by word
            words = prd_content.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield {
                    "type": "prd_chunk",
                    "chunk": chunk,
                    "message": f"📝 {chunk[:50]}..." if i % 10 == 0 else None
                }
                await asyncio.sleep(0.03)
            
            # Save final PRD
            product.final_prd = prd_content
            product.status = ProductStatus.IN_REVIEW
            self.db.commit()
            
            yield {
                "type": "prd_complete",
                "message": "✅ Final PRD generated successfully!"
            }
            
            # Final complete event
            yield {
                "type": "complete",
                "product_id": str(product.id),
                "message": "🎉 Product generation complete!",
                "outputs": {
                    "strategist": product.strategist_output,
                    "market_research": product.market_research_output,
                    "prd": product.prd_output,
                    "tech_architecture": product.tech_architecture,
                    "ux_design": product.ux_design,
                    "qa_strategy": product.qa_strategy,
                    "final_prd": product.final_prd
                }
            }
            
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            self.db.rollback()
            yield {
                "type": "error",
                "error": str(e)
            }
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        try:
            from uuid import UUID
            product_uuid = UUID(product_id)
            product = self.db.query(Product).filter(Product.id == product_uuid).first()
        except Exception as e:
            logger.error(f"Error parsing product_id: {e}")
            return None
            
        if not product:
            return None
        
        return {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "idea": product.idea,
            "status": product.status.value if hasattr(product.status, 'value') else product.status,
            "strategist_output": product.strategist_output,
            "market_research_output": product.market_research_output,
            "prd_output": product.prd_output,
            "tech_architecture": product.tech_architecture,
            "ux_design": product.ux_design,
            "qa_strategy": product.qa_strategy,
            "final_prd": product.final_prd,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }