
"""Agent Influence Broker - User Model"""

from datetime import datetime
from uuid import uuid4

try:
    from sqlalchemy import Column, String, Integer, Boolean, DateTime
    from app.core.database import Base
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = object

if SQLALCHEMY_AVAILABLE:
    class User(Base):
        """User model with authentication and profile management."""
        __tablename__ = "users"
        
        id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
        email = Column(String(255), unique=True, nullable=False)
        username = Column(String(50), unique=True, nullable=False)
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.utcnow)
else:
    class User:
        """Fallback User class."""
        def __init__(self, **kwargs):
            self.id = str(uuid4())
            self.email = kwargs.get('email')
            self.username = kwargs.get('username')
