"""
Customer database model.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Customer(Base):
    """Customer model for user management."""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(255))
    
    # Relationships
    orders = relationship("Order", back_populates="customer") 