from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.session import Session as SessionModel
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseTools:
    """Database operations for agents."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_product(self, product_data: Dict[str, Any]) -> Product:
        """Save or update product."""
        try:
            product_id = product_data.get("id")
            
            if product_id:
                product = self.db.query(Product).filter(Product.id == product_id).first()
                if product:
                    for key, value in product_data.items():
                        if hasattr(product, key) and value is not None:
                            setattr(product, key, value)
            else:
                product = Product(**product_data)
                self.db.add(product)
            
            self.db.commit()
            self.db.refresh(product)
            return product
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save product: {e}")
            raise
    
    def save_session_state(self, product_id: str, state: Dict[str, Any], current_node: str) -> SessionModel:
        """Save agent session state."""
        try:
            session = self.db.query(SessionModel).filter(
                SessionModel.product_id == product_id
            ).first()
            
            if session:
                session.state = state
                session.current_node = current_node
            else:
                session = SessionModel(
                    product_id=product_id,
                    state=state,
                    current_node=current_node
                )
                self.db.add(session)
            
            self.db.commit()
            self.db.refresh(session)
            return session
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save session: {e}")
            raise
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()