# in tenxagent/history.py

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List
from .schemas import Message

# For MongoDB, we need an async client like motor
try:
    import motor.motor_asyncio
except ImportError:
    motor = None # Handle optional dependency

class HistoryStore(ABC):
    """Abstract base class for all message history stores."""
    
    @abstractmethod
    async def get_messages(self, session_id: str) -> List[Message]:
        """Retrieve all messages for a given session."""
        pass

    @abstractmethod
    async def add_message(self, session_id: str, message: Message):
        """Add a new message to a session's history."""
        pass

    async def clear_history(self, session_id: str):
        """Optional: Clear a session's history."""
        raise NotImplementedError

# --- Implementation 1: In-Memory Store (Default) ---

class InMemoryHistoryStore(HistoryStore):
    """A simple thread-safe, in-memory message history store."""
    def __init__(self):
        self._history = defaultdict(list)

    async def get_messages(self, session_id: str) -> List[Message]:
        return self._history[session_id][:] # Return a copy

    async def add_message(self, session_id: str, message: Message):
        self._history[session_id].append(message)

    async def clear_history(self, session_id: str):
        if session_id in self._history:
            del self._history[session_id]

# --- Implementation 2: MongoDB Store ---

class MongoHistoryStore(HistoryStore):
    """A persistent message history store using MongoDB Atlas."""
    def __init__(self, connection_string: str, database: str, collection: str):
        if motor is None:
            raise ImportError("The 'motor' library is required for MongoHistoryStore. Please install it with 'pip install motor'.")
        
        self.client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
        self.db = self.client[database]
        self.collection = self.db[collection]

    async def get_messages(self, session_id: str) -> List[Message]:
        document = await self.collection.find_one({"_id": session_id})
        if document and "messages" in document:
            # Convert list of dicts back to list of Pydantic Message objects
            return [Message(**msg) for msg in document["messages"]]
        return []

    async def add_message(self, session_id: str, message: Message):
        await self.collection.update_one(
            {"_id": session_id},
            {"$push": {"messages": message.model_dump()}},
            upsert=True
        )

    async def clear_history(self, session_id: str):
        await self.collection.delete_one({"_id": session_id})