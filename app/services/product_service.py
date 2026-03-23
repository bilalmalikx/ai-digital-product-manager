from sqlalchemy.orm import Session
from app.models.product import Product, ProductStatus
from app.models.session import Session as SessionModel
from app.core.graph import build_graph
from app.tools.database_tools import DatabaseTools
from app.tools.mcp_tools import mcp_tools
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

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
                    "qa_strategy": product.qa_strategy
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
            
            return {
                "product_id": str(product.id),
                "status": product.status,
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
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        product = self.db_tools.get_product(product_id)
        if not product:
            return None
        
        return {
            "id": str(product.id),
            "name": product.name,
            "idea": product.idea,
            "status": product.status,
            "outputs": {
                "strategist": product.strategist_output,
                "market_research": product.market_research_output,
                "prd": product.prd_output,
                "tech_architecture": product.tech_architecture,
                "ux_design": product.ux_design,
                "qa_strategy": product.qa_strategy,
                "final_prd": product.final_prd
            },
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }