"""
Category database model.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Category(Base):
    """Category model for product categorization."""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    
    # Relationships
    clothes = relationship("Clothes", back_populates="category") 