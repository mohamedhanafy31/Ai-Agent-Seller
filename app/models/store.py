"""
Store database model.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Store(Base):
    """Store model for retail locations."""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255))
    
    # Relationships
    clothes = relationship("Clothes", back_populates="store") 