"""
SQLAlchemy models for Broadie persistence.
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Conversation(Base):
    """Conversation/Thread model for organizing messages."""

    __tablename__ = "conversations"

    id = Column(String, primary_key=True)  # thread_id
    title = Column(String, nullable=False, default="New Conversation")
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    agent = relationship("Agent", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    todos = relationship(
        "Todo", back_populates="conversation", cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "agent_id": self.agent_id,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": 0,  # Will be calculated separately to avoid lazy loading
        }


class Agent(Base):
    """Agent model for storing agent configurations."""

    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    memories = relationship(
        "Memory", back_populates="agent", cascade="all, delete-orphan"
    )
    messages = relationship(
        "Message", back_populates="agent", cascade="all, delete-orphan"
    )
    conversations = relationship(
        "Conversation", back_populates="agent", cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Memory(Base):
    """Memory model for storing agent memories."""

    __tablename__ = "memories"

    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    content = Column(Text, nullable=False)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    agent = relationship("Agent", back_populates="memories")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "content": self.content,
            "metadata": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Todo(Base):
    """Todo model for tracking agent-generated tasks."""

    __tablename__ = "todos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(
        String, ForeignKey("conversations.id"), nullable=False, index=True
    )
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True, index=True)
    description = Column(Text, nullable=False)
    status = Column(
        String, default="pending", nullable=False, index=True
    )  # pending, in_progress, done
    assigned_to = Column(String, nullable=True)  # agent name or external assignee
    source_tool = Column(String, nullable=True)  # tool that generated the todo
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="todos")
    message = relationship("Message", back_populates="todos")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "message_id": self.message_id,
            "description": self.description,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "source_tool": self.source_tool,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Message(Base):
    """Message model for storing conversation messages."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(
        String, ForeignKey("conversations.id"), nullable=False, index=True
    )
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(String, nullable=False)  # Keep as string for compatibility
    created_at = Column(DateTime, default=func.now())

    # Relationships
    agent = relationship("Agent", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
    todos = relationship("Todo", back_populates="message", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "agent_id": self.agent_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
