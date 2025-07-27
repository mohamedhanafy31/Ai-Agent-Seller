"""
Base database configuration and imports.
"""

# Import all SQLAlchemy models here so that they are registered with SQLAlchemy
from app.models.category import Category  # noqa
from app.models.store import Store  # noqa
from app.models.clothes import Clothes  # noqa
from app.models.customer import Customer  # noqa
from app.models.order import Order, OrderItem  # noqa

from app.db.base_class import Base  # noqa 