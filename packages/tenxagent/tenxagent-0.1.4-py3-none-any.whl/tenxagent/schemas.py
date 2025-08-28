# in tenxagent/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]
     
class Message(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

# A schema to standardize the output from any language model
class GenerationResult(BaseModel):
    message: Message
    input_tokens: int
    output_tokens: int

