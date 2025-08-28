# in flexi_agent/agent.py
from .models import LanguageModel
from .tools import Tool
from .schemas import Message, GenerationResult, ToolCall 
from typing import List, Optional, Dict, Any, Type, Union
from .history import HistoryStore, InMemoryHistoryStore
from pydantic import BaseModel, Field
import json
import asyncio



class TenxAgent:
    def __init__(
        self,
        llm: LanguageModel,
        tools: List[Tool],
        system_prompt: str = None,
        max_llm_calls: int = 10, # RENAMED for clarity
        max_tokens: int = 4096,
        history_store: HistoryStore = None,
        output_model: Optional[Type[BaseModel]] = None,
    ):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.user_system_prompt = system_prompt
        self.max_llm_calls = max_llm_calls
        self.max_tokens = max_tokens
        self.history_store = history_store or InMemoryHistoryStore()
        self.output_model = output_model

    def _get_system_prompt(self) -> str:
        """Get the system prompt from the LLM model, which handles tool calling instructions."""
        tools_list = list(self.tools.values()) if self.tools else None
        
        # Get base prompt from LLM
        base_prompt = self.llm.get_tool_calling_system_prompt(tools=tools_list, user_prompt=self.user_system_prompt)
        
        # Add structured output instructions if output model is specified
        if self.output_model:
            # Get field descriptions and create clear instructions
            field_descriptions = []
            for field_name, field_info in self.output_model.model_fields.items():
                field_type = field_info.annotation
                description = field_info.description or "No description provided"
                default_val = getattr(field_info, 'default', None)
                
                # Handle enum types specially
                if hasattr(field_type, '__origin__') and hasattr(field_type, '__args__'):
                    # Handle Optional types
                    inner_type = field_type.__args__[0] if field_type.__args__ else field_type
                    if hasattr(inner_type, '__members__'):  # It's an enum
                        enum_values = list(inner_type.__members__.keys())
                        field_descriptions.append(f"  - {field_name}: Must be one of {enum_values}. {description}")
                    else:
                        field_descriptions.append(f"  - {field_name}: {field_type}. {description}")
                elif hasattr(field_type, '__members__'):  # Direct enum
                    enum_values = list(field_type.__members__.keys())
                    field_descriptions.append(f"  - {field_name}: Must be one of {enum_values}. {description}")
                else:
                    field_descriptions.append(f"  - {field_name}: {field_type}. {description}")
            
            # Create a realistic example
            try:
                sample_instance = self.output_model()
                sample_json = sample_instance.model_dump()
                # Make the example more realistic
                if 'message' in sample_json:
                    sample_json['message'] = "This is an example response message"
                if 'type' in sample_json and hasattr(self.output_model.model_fields['type'].annotation, '__members__'):
                    # Use the first enum value as example
                    first_enum_value = list(self.output_model.model_fields['type'].annotation.__members__.keys())[0]
                    sample_json['type'] = first_enum_value
            except Exception:
                sample_json = {"error": "Could not create example"}
            
            output_instructions = f"""

CRITICAL: You must respond with ONLY valid JSON in this exact format:

Required fields:
{chr(10).join(field_descriptions)}

Example response:
{json.dumps(sample_json, indent=2)}

RULES:
1. Response must be valid JSON only - no extra text, explanations, or markdown
2. All required fields must be present
3. Use exact enum values as specified (e.g., "text", "radio", etc.)
4. Follow the field descriptions carefully
5. Start your response with {{ and end with }}"""
            
            return base_prompt + output_instructions
        
        return base_prompt

    async def _execute_tool(self, tool_call: ToolCall, metadata: Dict[str, Any]) -> Message:
        """Helper to execute a single tool call and return a tool message."""
        tool = self.tools.get(tool_call.name)
        if not tool:
            result_content = f"Error: Tool '{tool_call.name}' not found."
        else:
            try:
                validated_args = tool.args_schema(**tool_call.arguments)
                result_content = await asyncio.to_thread(tool.execute, metadata=metadata, **validated_args.model_dump())
            except Exception as e:
                result_content = f"Error executing tool '{tool_call.name}': {e}"
        
        return Message(role="tool", content=result_content, tool_call_id=tool_call.id) # Assumes ToolCall has an ID

    async def run(self, user_input: str, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> Union[str, BaseModel]:
        metadata = metadata or {}
        llm_calls_count = 0
        total_tokens_used = 0
        messages = await self.history_store.get_messages(session_id)

        user_message = Message(role="user", content=user_input)
        await self.history_store.add_message(session_id, user_message)
        messages.append(user_message)
        
        if not any(msg.role == "system" for msg in messages):
            messages.insert(0, Message(role="system", content=self._get_system_prompt()))

        while True:
            if llm_calls_count >= self.max_llm_calls:
                return "Error: Maximum number of LLM calls reached."
            
            llm_calls_count += 1
            
            # Pass tools to the LLM (it will handle the conversion to its own format)
            tools_list = list(self.tools.values()) if self.tools else None
            generation_result = await self.llm.generate(messages, tools=tools_list, metadata=metadata)
            
            total_tokens_used += generation_result.input_tokens + generation_result.output_tokens
            if total_tokens_used >= self.max_tokens:
                return "Error: Token limit reached."
            
            response_message = generation_result.message
            await self.history_store.add_message(session_id, response_message)
            messages.append(response_message)
            
            # --- NEW: PARALLEL TOOL CALL LOGIC ---
            if response_message.tool_calls:
                # 1. Create a task for each tool call requested by the LLM
                execution_tasks = [
                    self._execute_tool(tool_call, metadata) for tool_call in response_message.tool_calls
                ]
                
                # 2. Run all tool calls concurrently
                tool_result_messages = await asyncio.gather(*execution_tasks)
                
                # 3. Add all results to history and continue the loop
                for msg in tool_result_messages:
                    await self.history_store.add_message(session_id, msg)
                    messages.append(msg)
                
                continue # Go back to the LLM with the tool results
            
            # If there are no tool calls, we have our final answer
            final_content = response_message.content or "The agent finished without a final message."
            
            # If output model is specified, validate and parse the response
            if self.output_model:
                try:
                    # Try to parse as JSON first
                    if final_content.strip().startswith('{') and final_content.strip().endswith('}'):
                        import json
                        parsed_json = json.loads(final_content)
                        validated_output = self.output_model(**parsed_json)
                        return validated_output  # Return the Pydantic model instance
                    else:
                        # Content might have extra text, try to extract JSON
                        import re
                        json_match = re.search(r'\{.*\}', final_content, re.DOTALL)
                        if json_match:
                            parsed_json = json.loads(json_match.group())
                            validated_output = self.output_model(**parsed_json)
                            return validated_output  # Return the Pydantic model instance
                        else:
                            return f"Error: Response does not match required output format. Expected JSON matching {self.output_model.__name__} schema."
                except json.JSONDecodeError as e:
                    return f"Error: Invalid JSON in response: {str(e)}"
                except Exception as e:
                    return f"Error: Response validation failed: {str(e)}"
            
            return final_content

class AgentToolInput(BaseModel):
    task: str = Field(description="The specific task for the agent to perform.")

def create_tenx_agent_tool(agent: TenxAgent, name: str, description: str) -> Tool:
    """Wraps an Agent to be used as a Tool by another Agent."""
    
    class AgentAsTool(Tool):
        def __init__(self, agent_instance, tool_name, tool_description):
            self.name = tool_name
            self.description = tool_description
            self.args_schema = AgentToolInput
            self.agent = agent_instance

        def execute(self, task: str, metadata: dict = None) -> str:
            import asyncio
            import uuid
            
            # Generate a unique session ID for this tool execution
            session_id = f"agent_tool_{uuid.uuid4().hex[:8]}"
            
            # Simple approach: just run the async function
            try:
                return asyncio.run(self.agent.run(task, session_id=session_id, metadata=metadata))
            except RuntimeError as e:
                if "cannot be called from a running event loop" in str(e):
                    # We're in an async context, use a thread
                    import threading
                    import queue
                    
                    result_queue = queue.Queue()
                    
                    def run_in_thread():
                        try:
                            result = asyncio.run(self.agent.run(task, session_id=session_id, metadata=metadata))
                            result_queue.put(('success', result))
                        except Exception as e:
                            result_queue.put(('error', e))
                    
                    thread = threading.Thread(target=run_in_thread)
                    thread.start()
                    thread.join()
                    
                    status, result = result_queue.get()
                    if status == 'error':
                        raise result
                    return result
                else:
                    raise e
            
    return AgentAsTool(agent, name, description)