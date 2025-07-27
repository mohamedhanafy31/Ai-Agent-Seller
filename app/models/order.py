"""
Order and OrderItem database models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Order(Base):
    """Order model for purchase transactions."""
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """OrderItem model for individual items in an order."""
    
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    clothes_id = Column(Integer, ForeignKey("clothes.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    clothes = relationship("Clothes", back_populates="order_items") 