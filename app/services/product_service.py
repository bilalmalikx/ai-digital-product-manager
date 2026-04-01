# app/services/product_service.py
from sqlalchemy.orm import Session
from app.models.product import Product, ProductStatus
from app.models.session import Session as SessionModel
from app.core.graph import build_graph
from app.agents.final_prd_writer import create_final_prd_writer_node
from app.tools.database_tools import DatabaseTools
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
        """Generate complete product documentation with all agents including Final PRD Writer."""
        
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
            
            # Run the graph with all agents including Final PRD Writer
            final_state = await self.graph.ainvoke(initial_state)
            
            # Update product with all outputs
            product.strategist_output = final_state.get("strategist_output")
            product.market_research_output = final_state.get("market_research_output")
            product.prd_output = final_state.get("prd_output")
            product.tech_architecture = final_state.get("tech_architecture")
            product.ux_design = final_state.get("ux_design")
            product.qa_strategy = final_state.get("qa_strategy")
            
            # Extract final PRD (from FinalPRDWriterAgent)
            final_prd_data = final_state.get("final_prd")
            if final_prd_data:
                if isinstance(final_prd_data, dict):
                    # If it's a JSON dict, convert to formatted string
                    product.final_prd = json.dumps(final_prd_data, indent=2)
                else:
                    product.final_prd = str(final_prd_data)
            else:
                # Fallback: generate basic PRD
                product.final_prd = self._generate_basic_prd(product)
            
            product.status = ProductStatus.IN_REVIEW
            
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
    
    def _generate_basic_prd(self, product: Product) -> str:
        """Fallback PRD generation if agent fails."""
        return f"""
# Product Requirements Document

## Product Name: {product.name}

## Original Idea: {product.idea}

## Executive Summary
This document outlines the product requirements for {product.name}.

## Features
Based on the initial idea, the product will include:
- Core functionality as described in the idea
- User management and authentication
- Data persistence and storage
- API integration capabilities

## Technical Considerations
- Scalable architecture
- Security best practices
- Performance optimization

## Timeline
To be determined based on detailed requirements.

*Note: This is an automatically generated PRD. For detailed specifications, please run the complete agent workflow.*
"""
    
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
            
            # Define agents in order - INCLUDING FINAL PRD WRITER
            agents = [
                ("strategist_node", "strategist_output", "📊 Strategist analyzing market..."),
                ("market_research_node", "market_research_output", "🔍 Conducting market research..."),
                ("prd_node", "prd_output", "📋 Generating PRD..."),
                ("tech_architecture_node", "tech_architecture", "🏗️ Designing tech architecture..."),
                ("ux_design_node", "ux_design", "🎨 Creating UX design..."),
                ("qa_strategy_node", "qa_strategy", "🧪 Developing QA strategy..."),
                ("final_prd_writer_node", "final_prd", "📝 Generating final comprehensive PRD...")
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
                
                await asyncio.sleep(1.5)
                
                # Mock output with real structure
                if agent_name == "strategist_node":
                    mock_output = {
                        "market_positioning": "Premium AI-powered solution targeting enterprise customers",
                        "target_users": ["CTOs", "Product Managers", "Software Architects"],
                        "strategy": "Differentiate through AI automation and seamless integration",
                        "competitive_advantage": "Native AI integration with existing workflows"
                    }
                elif agent_name == "market_research_node":
                    mock_output = {
                        "competitors": [{"name": "Competitor A", "strength": "Market share", "weakness": "High cost"}],
                        "market_size": "$5B and growing at 25% CAGR",
                        "trends": ["AI adoption", "Automation", "Low-code platforms"],
                        "opportunities": ["Untapped SMB segment", "Integration gap"],
                        "threats": ["New entrants", "Price pressure"]
                    }
                elif agent_name == "prd_node":
                    mock_output = {
                        "features": [
                            {"name": "User Auth", "priority": "P0", "description": "Secure authentication"},
                            {"name": "Agent Workflow", "priority": "P0", "description": "Multi-agent orchestration"},
                            {"name": "Analytics", "priority": "P1", "description": "Usage metrics"}
                        ],
                        "requirements": ["Scalable architecture", "99.9% uptime"],
                        "user_stories": ["As a user, I want to generate PRDs automatically"],
                        "success_metrics": ["50% reduction in documentation time"]
                    }
                elif agent_name == "tech_architecture_node":
                    mock_output = {
                        "tech_stack": {
                            "backend": ["FastAPI", "PostgreSQL", "Redis"],
                            "frontend": ["Angular", "Tailwind"],
                            "infrastructure": ["Docker", "AWS"]
                        },
                        "system_design": "Microservices architecture with event-driven communication",
                        "api_endpoints": ["/api/v1/generate", "/api/v1/products"],
                        "database_schema": [{"table": "products", "columns": ["id", "idea", "final_prd"]}],
                        "security_considerations": ["JWT auth", "Rate limiting", "Data encryption"]
                    }
                elif agent_name == "ux_design_node":
                    mock_output = {
                        "user_flows": [{"flow_name": "PRD Generation", "steps": ["Input idea", "Review outputs", "Export PRD"]}],
                        "key_screens": ["Dashboard", "Generator", "History"],
                        "design_system": {"colors": ["primary-blue", "secondary-gray"]},
                        "accessibility": ["WCAG 2.1 AA compliant"]
                    }
                elif agent_name == "qa_strategy_node":
                    mock_output = {
                        "test_cases": [{"name": "PRD Generation", "steps": ["Enter idea", "Verify output format"]}],
                        "testing_approach": "Automated testing with 80% coverage",
                        "automation_strategy": "CI/CD pipeline with GitHub Actions",
                        "performance_benchmarks": ["< 2s response time", "100 concurrent users"]
                    }
                elif agent_name == "final_prd_writer_node":
                    mock_output = {
                        "product_name": product.name,
                        "executive_summary": {
                            "vision": "AI-powered product documentation automation",
                            "problem_statement": "Product managers spend 40% time on documentation",
                            "target_users": ["Product Managers", "CTOs", "Technical Writers"]
                        },
                        "features": [
                            {"id": "F1", "name": "Auto PRD Generation", "priority": "P0", "effort": "High"},
                            {"id": "F2", "name": "Multi-agent Workflow", "priority": "P0", "effort": "Medium"},
                            {"id": "F3", "name": "Export Options", "priority": "P1", "effort": "Low"}
                        ],
                        "technical_specifications": {
                            "backend_apis": [{"endpoint": "/api/v1/generate", "method": "POST"}],
                            "tech_stack": {"backend": ["FastAPI"], "frontend": ["Angular"]}
                        },
                        "timeline": {
                            "phase_1_mvp": {"duration": "4 weeks", "features": ["F1"]},
                            "phase_2": {"duration": "6 weeks", "features": ["F2", "F3"]}
                        },
                        "success_metrics": [
                            {"metric": "Time saved", "target": "50% reduction"},
                            {"metric": "User adoption", "target": "1000 users in Q1"}
                        ]
                    }
                else:
                    mock_output = {
                        "status": "completed",
                        "timestamp": datetime.utcnow().isoformat(),
                        "analysis": f"Detailed analysis from {agent_name}",
                        "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
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
                    product.final_prd = json.dumps(mock_output, indent=2)
                
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