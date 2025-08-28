"""
Unified SQLAlchemy backend for Broadie persistence.
Supports SQLite, PostgreSQL, and other SQLAlchemy-compatible databases.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from ..utils.exceptions import PersistenceError
from .models import Agent, Base, Conversation, Memory, Message, Todo


class SQLAlchemyBackend:
    """Unified SQLAlchemy storage backend."""

    def __init__(self, database_url: str):
        """Initialize with database URL.

        Examples:
        - SQLite: "sqlite+aiosqlite:///./broadie.db"
        - PostgreSQL: "postgresql+asyncpg://user:password@localhost/dbname"
        - MySQL: "mysql+aiomysql://user:password@localhost/dbname"
        """
        self.database_url = database_url
        self.engine = None
        self.async_session = None

    async def initialize(self):
        """Initialize database engine and create tables."""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,  # Verify connections before use
            )

            # Create session factory
            self.async_session = async_sessionmaker(
                bind=self.engine, class_=AsyncSession, expire_on_commit=False
            )

            # Create all tables and run lightweight migrations
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # Best-effort: add 'summary' column if missing (SQLite/Postgres compatible)
                try:
                    await conn.exec_driver_sql(
                        "ALTER TABLE conversations ADD COLUMN summary TEXT"
                    )
                except Exception:
                    # Ignore if column already exists or dialect doesn't support this syntax
                    pass

        except Exception as e:
            raise PersistenceError(f"Failed to initialize database: {e}")

    @asynccontextmanager
    async def get_session(self):
        """Get database session context manager."""
        if not self.async_session:
            raise PersistenceError("Backend not initialized")

        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def store_agent(
        self, agent_id: str, name: str, config: Dict[str, Any]
    ) -> bool:
        """Store agent configuration."""
        try:
            async with self.get_session() as session:
                # Check if agent exists
                stmt = select(Agent).where(Agent.id == agent_id)
                result = await session.execute(stmt)
                agent = result.scalar_one_or_none()

                if agent:
                    # Update existing agent
                    agent.name = name
                    agent.config = config
                else:
                    # Create new agent
                    agent = Agent(id=agent_id, name=name, config=config)
                    session.add(agent)

                return True
        except Exception as e:
            raise PersistenceError(f"Failed to store agent: {e}")

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent configuration."""
        try:
            async with self.get_session() as session:
                stmt = select(Agent).where(Agent.id == agent_id)
                result = await session.execute(stmt)
                agent = result.scalar_one_or_none()

                if agent:
                    return {"name": agent.name, "config": agent.config}
                return None
        except Exception as e:
            raise PersistenceError(f"Failed to retrieve agent: {e}")

    async def get_agent_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent by name."""
        try:
            async with self.get_session() as session:
                stmt = (
                    select(Agent)
                    .where(Agent.name == name)
                    .order_by(Agent.created_at.desc())
                )
                result = await session.execute(stmt)
                agent = result.scalar_one_or_none()

                if agent:
                    return {"id": agent.id, "name": agent.name, "config": agent.config}
                return None
        except Exception as e:
            raise PersistenceError(f"Failed to retrieve agent by name: {e}")

    async def store_memory(
        self,
        memory_id: str,
        agent_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Store memory."""
        try:
            async with self.get_session() as session:
                memory = Memory(
                    id=memory_id, agent_id=agent_id, content=content, meta_data=metadata
                )
                session.add(memory)
                return True
        except Exception as e:
            raise PersistenceError(f"Failed to store memory: {e}")

    async def get_memories(self, agent_id: str) -> List[Dict[str, Any]]:
        """Retrieve memories for an agent."""
        try:
            async with self.get_session() as session:
                stmt = (
                    select(Memory)
                    .where(Memory.agent_id == agent_id)
                    .order_by(Memory.created_at)
                )
                result = await session.execute(stmt)
                memories = result.scalars().all()

                return [memory.to_dict() for memory in memories]
        except Exception as e:
            raise PersistenceError(f"Failed to retrieve memories: {e}")

    async def store_message(
        self,
        conversation_id: str,
        agent_id: str,
        role: str,
        content: str,
        timestamp: str,
    ) -> bool:
        """Store a single conversation message."""
        try:
            async with self.get_session() as session:
                message = Message(
                    conversation_id=conversation_id,
                    agent_id=agent_id,
                    role=role,
                    content=content,
                    timestamp=timestamp,
                )
                session.add(message)
                return True
        except Exception as e:
            raise PersistenceError(f"Failed to store message: {e}")

    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve all messages for a conversation, ordered by insertion."""
        try:
            async with self.get_session() as session:
                stmt = (
                    select(Message)
                    .where(Message.conversation_id == conversation_id)
                    .order_by(Message.id)
                )
                result = await session.execute(stmt)
                messages = result.scalars().all()

                return [message.to_dict() for message in messages]
        except Exception as e:
            raise PersistenceError(f"Failed to retrieve messages: {e}")

    async def create_conversation(
        self,
        conversation_id: str,
        agent_id: str,
        title: str = "New Conversation",
        summary: Optional[str] = None,
    ) -> bool:
        """Create a new conversation."""
        try:
            async with self.get_session() as session:
                conversation = Conversation(
                    id=conversation_id, title=title, agent_id=agent_id, summary=summary
                )
                session.add(conversation)
                return True
        except Exception as e:
            raise PersistenceError(f"Failed to create conversation: {e}")

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID."""
        try:
            async with self.get_session() as session:
                stmt = select(Conversation).where(Conversation.id == conversation_id)
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()

                if conversation:
                    return conversation.to_dict()
                return None
        except Exception as e:
            raise PersistenceError(f"Failed to retrieve conversation: {e}")

    async def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title."""
        try:
            async with self.get_session() as session:
                stmt = select(Conversation).where(Conversation.id == conversation_id)
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()

                if conversation:
                    conversation.title = title
                    return True
                return False
        except Exception as e:
            raise PersistenceError(f"Failed to update conversation title: {e}")

    async def update_conversation_summary(
        self, conversation_id: str, summary: Optional[str]
    ) -> bool:
        """Update conversation summary."""
        try:
            async with self.get_session() as session:
                stmt = select(Conversation).where(Conversation.id == conversation_id)
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()
                if conversation:
                    conversation.summary = summary
                    return True
                return False
        except Exception as e:
            raise PersistenceError(f"Failed to update conversation summary: {e}")

    async def list_conversations(
        self, agent_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List conversations with optional agent filter."""
        try:
            async with self.get_session() as session:
                # Get conversations with message counts
                stmt = (
                    select(Conversation, func.count(Message.id).label("message_count"))
                    .outerjoin(Message)
                    .group_by(Conversation.id)
                    .order_by(Conversation.updated_at.desc())
                )

                if agent_id:
                    stmt = stmt.where(Conversation.agent_id == agent_id)

                stmt = stmt.limit(limit)

                result = await session.execute(stmt)
                results = result.all()

                conversations = []
                for conv, msg_count in results:
                    conv_dict = conv.to_dict()
                    conv_dict["message_count"] = msg_count
                    conversations.append(conv_dict)

                return conversations
        except Exception as e:
            raise PersistenceError(f"Failed to list conversations: {e}")

    async def create_todo(
        self,
        conversation_id: str,
        description: str,
        message_id: Optional[int] = None,
        assigned_to: Optional[str] = None,
        source_tool: Optional[str] = None,
        status: str = "pending",
    ) -> str:
        """Create a new todo and return its ID."""
        try:
            async with self.get_session() as session:
                todo = Todo(
                    conversation_id=conversation_id,
                    message_id=message_id,
                    description=description,
                    status=status,
                    assigned_to=assigned_to,
                    source_tool=source_tool,
                )
                session.add(todo)
                await session.flush()  # Get the ID
                return todo.id
        except Exception as e:
            raise PersistenceError(f"Failed to create todo: {e}")

    async def get_todos(
        self,
        conversation_id: Optional[str] = None,
        message_id: Optional[int] = None,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve todos with optional filters."""
        try:
            async with self.get_session() as session:
                stmt = select(Todo)

                if conversation_id:
                    stmt = stmt.where(Todo.conversation_id == conversation_id)
                if message_id:
                    stmt = stmt.where(Todo.message_id == message_id)
                if status:
                    stmt = stmt.where(Todo.status == status)
                if assigned_to:
                    stmt = stmt.where(Todo.assigned_to == assigned_to)

                stmt = stmt.order_by(Todo.created_at.desc())

                result = await session.execute(stmt)
                todos = result.scalars().all()

                return [todo.to_dict() for todo in todos]
        except Exception as e:
            raise PersistenceError(f"Failed to retrieve todos: {e}")

    async def update_todo_status(
        self, todo_id: str, status: str, assigned_to: Optional[str] = None
    ) -> bool:
        """Update todo status and optionally assigned_to."""
        try:
            async with self.get_session() as session:
                stmt = select(Todo).where(Todo.id == todo_id)
                result = await session.execute(stmt)
                todo = result.scalar_one_or_none()

                if not todo:
                    return False

                todo.status = status
                if assigned_to is not None:
                    todo.assigned_to = assigned_to

                return True
        except Exception as e:
            raise PersistenceError(f"Failed to update todo status: {e}")

    async def get_todo_by_id(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific todo by ID."""
        try:
            async with self.get_session() as session:
                stmt = select(Todo).where(Todo.id == todo_id)
                result = await session.execute(stmt)
                todo = result.scalar_one_or_none()

                if todo:
                    return todo.to_dict()
                return None
        except Exception as e:
            raise PersistenceError(f"Failed to retrieve todo: {e}")

    async def store_message_with_metadata(
        self,
        conversation_id: str,
        agent_id: str,
        role: str,
        content: str,
        timestamp: str,
        todos_created: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """Store a message and return its ID, optionally creating associated todos."""
        try:
            async with self.get_session() as session:
                # Create message
                message = Message(
                    conversation_id=conversation_id,
                    agent_id=agent_id,
                    role=role,
                    content=content,
                    timestamp=timestamp,
                )
                session.add(message)
                await session.flush()  # Get the message ID

                message_id = message.id

                # Create associated todos if provided
                if todos_created:
                    for todo_data in todos_created:
                        todo = Todo(
                            conversation_id=conversation_id,
                            message_id=message_id,
                            description=todo_data.get("description", ""),
                            status=todo_data.get("status", "pending"),
                            assigned_to=todo_data.get("assigned_to"),
                            source_tool=todo_data.get("source_tool", "agent"),
                        )
                        session.add(todo)

                return message_id
        except Exception as e:
            raise PersistenceError(f"Failed to store message with metadata: {e}")

    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
