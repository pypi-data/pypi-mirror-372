"""
Persistence module for Broadie.

Provides unified SQLAlchemy backend for SQLite, PostgreSQL, and other databases.
"""

from .sqlalchemy_backend import SQLAlchemyBackend
from .models import Base, Agent, Memory, Message, Todo, Conversation
from .migrations import MigrationManager, migrate_database, reset_database_schema

try:
    from .vector_store import VectorStore
except ImportError:
    # Optional dependency
    VectorStore = None

__all__ = [
    "SQLAlchemyBackend",
    "Base",
    "Agent",
    "Memory", 
    "Message",
    "Todo",
    "Conversation",
    "MigrationManager",
    "migrate_database",
    "reset_database_schema",
]
if VectorStore is not None:
    __all__.append("VectorStore")