"""
Clothes database model.
"""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Clothes(Base):
    """Clothes model for products."""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0, index=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="clothes")
    store = relationship("Store", back_populates="clothes")
    order_items = relationship("OrderItem", back_populates="clothes") 