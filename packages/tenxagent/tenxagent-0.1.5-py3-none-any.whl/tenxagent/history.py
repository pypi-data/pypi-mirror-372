# in tenxagent/history.py

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Type, TypeVar, Generic, Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
from .schemas import Message

# For MongoDB, we need an async client like motor
try:
    import motor.motor_asyncio
except ImportError:
    motor = None # Handle optional dependency

# Simple history store interface for standard Message objects
class HistoryStore(ABC):
    """Simple abstract base class for message history stores using standard Message format."""
    
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

# Generic type for custom message schemas
MessageType = TypeVar('MessageType', bound=BaseModel)

class FlexibleHistoryStore(ABC, Generic[MessageType]):
    """Abstract base class for external history stores with flexible message schemas."""
    
    def __init__(self, message_schema: Type[MessageType]):
        """Initialize with a custom message schema."""
        self.message_schema = message_schema
    
    @abstractmethod
    async def get_messages(self, session_id: str) -> List[MessageType]:
        """Retrieve all messages for a given session."""
        pass

    @abstractmethod
    async def add_message(self, session_id: str, message: MessageType):
        """Add a new message to a session's history."""
        pass

    async def clear_history(self, session_id: str):
        """Optional: Clear a session's history."""
        raise NotImplementedError
    
    def convert_to_standard_message(self, custom_message: MessageType) -> Message:
        """Convert custom message format to standard Message format for agent processing."""
        if isinstance(custom_message, Message):
            return custom_message
            
        # Extract standard fields from custom message
        message_dict = custom_message.model_dump()
        
        # Map common field names to standard Message fields
        role_mapping = {
            'sender': lambda x: 'assistant' if x == 'bot' else x,
            'type': lambda x: x,
            'role': lambda x: x
        }
        
        # Try to extract role/sender information
        role = 'user'  # default
        for field, mapper in role_mapping.items():
            if field in message_dict:
                mapped_value = mapper(message_dict[field])
                if mapped_value in ['user', 'assistant', 'system', 'tool']:
                    role = mapped_value
                    break
        
        # Extract content/message
        content = message_dict.get('message') or message_dict.get('content') or ''
        
        # Extract tool calls if present
        tool_calls = message_dict.get('tool_calls', [])
        tool_call_id = message_dict.get('tool_call_id')
        
        return Message(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id
        )
    
    def convert_from_standard_message(self, standard_message: Message, **extra_fields) -> MessageType:
        """Convert standard Message to custom message format."""
        # Get the fields that the custom schema expects
        schema_fields = self.message_schema.model_fields
        converted_data = {}
        
        # Map standard Message fields to custom schema
        field_mapping = {
            'role': ['role', 'sender', 'type'],
            'content': ['content', 'message', 'text'],
            'tool_calls': ['tool_calls'],
            'tool_call_id': ['tool_call_id']
        }
        
        for std_field, possible_custom_fields in field_mapping.items():
            std_value = getattr(standard_message, std_field, None)
            # Handle content field specially - ensure we always have a message
            if std_field == 'content':
                std_value = std_value or ""  # Ensure content is never None
            
            if std_value is not None:
                for custom_field in possible_custom_fields:
                    if custom_field in schema_fields:
                        # Special handling for role/sender mapping
                        if custom_field == 'sender' and std_field == 'role':
                            converted_data[custom_field] = 'bot' if std_value == 'assistant' else std_value
                        else:
                            converted_data[custom_field] = std_value
                        break
        
        # Add any extra fields provided
        converted_data.update(extra_fields)
        
        # Add default values for required fields not yet set
        for field_name, field_info in schema_fields.items():
            if field_name not in converted_data:
                # Check if field has a default value
                if hasattr(field_info, 'default') and field_info.default is not None and str(field_info.default) != 'PydanticUndefined':
                    converted_data[field_name] = field_info.default
                elif field_info.annotation == datetime:
                    converted_data[field_name] = datetime.utcnow()
                elif field_name == 'type':
                    # Map role to type for MongoMessage compatibility
                    converted_data[field_name] = standard_message.role
                # For required fields without defaults, try to provide reasonable values
                elif field_name in ['user_id', 'session_id', 'bot_id']:
                    converted_data[field_name] = extra_fields.get(field_name, 'unknown')
        
        return self.message_schema(**converted_data)

# --- Implementation 1: In-Memory Store (Default) ---

class InMemoryHistoryStore(HistoryStore):
    """A simple thread-safe, in-memory message history store using standard Message format."""
    def __init__(self):
        self._history = defaultdict(list)

    async def get_messages(self, session_id: str) -> List[Message]:
        return self._history[session_id][:] # Return a copy

    async def add_message(self, session_id: str, message: Message):
        self._history[session_id].append(message)

    async def clear_history(self, session_id: str):
        if session_id in self._history:
            del self._history[session_id]

# --- Implementation 2: MongoDB Store (Example Flexible Store) ---

class MongoHistoryStore(FlexibleHistoryStore[MessageType]):
    """A persistent message history store using MongoDB Atlas with flexible message schemas."""
    def __init__(self, connection_string: str, database: str, collection: str, message_schema: Type[MessageType]):
        super().__init__(message_schema)
        if motor is None:
            raise ImportError("The 'motor' library is required for MongoHistoryStore. Please install it with 'pip install motor'.")
        
        self.client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
        self.db = self.client[database]
        self.collection = self.db[collection]

    async def get_messages(self, session_id: str) -> List[MessageType]:
        document = await self.collection.find_one({"_id": session_id})
        if document and "messages" in document:
            # Convert list of dicts back to list of custom message objects
            return [self.message_schema(**msg) for msg in document["messages"]]
        return []

    async def add_message(self, session_id: str, message: MessageType):
        await self.collection.update_one(
            {"_id": session_id},
            {"$push": {"messages": message.model_dump()}},
            upsert=True
        )

    async def clear_history(self, session_id: str):
        await self.collection.delete_one({"_id": session_id})