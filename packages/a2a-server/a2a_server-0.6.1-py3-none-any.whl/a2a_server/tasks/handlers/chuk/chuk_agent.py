# a2a_server/tasks/handlers/chuk/chuk_agent.py
"""
Pure ChukAgent class with cleaned up logging levels.
"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# chuk-llm imports
from chuk_llm.llm.client import get_client
from chuk_llm.llm.system_prompt_generator import SystemPromptGenerator

# chuk-tool-processor imports
from chuk_tool_processor.registry.provider import ToolRegistryProvider
from chuk_tool_processor.mcp.setup_mcp_stdio import setup_mcp_stdio
from chuk_tool_processor.mcp.setup_mcp_sse import setup_mcp_sse
from chuk_tool_processor.execution.tool_executor import ToolExecutor
from chuk_tool_processor.execution.strategies.inprocess_strategy import InProcessStrategy
from chuk_tool_processor.models.tool_call import ToolCall

# Internal session management (optional)
try:
    from chuk_ai_session_manager import SessionManager as AISessionManager
    from chuk_ai_session_manager.session_storage import setup_chuk_sessions_storage
    HAS_SESSION_SUPPORT = True
except ImportError:
    HAS_SESSION_SUPPORT = False

logger = logging.getLogger(__name__)


class ChukAgent:
    """
    Pure ChukAgent with cleaned up logging levels for better readability.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        instruction: str = "",
        provider: str = "openai",
        model: Optional[str] = None,
        use_system_prompt_generator: bool = False,
        
        # MCP Configuration
        mcp_config_file: Optional[str] = None,
        mcp_servers: Optional[List[str]] = None,
        mcp_transport: str = "stdio",
        mcp_sse_servers: Optional[List[Dict[str, str]]] = None,
        tool_namespace: str = "tools",
        max_concurrency: int = 4,
        tool_timeout: float = 30.0,
        enable_tools: bool = True,
        
        # Debug settings
        debug_tools: bool = True,
        
        # Agent-internal session management (optional)
        enable_sessions: bool = True,
        infinite_context: bool = True,
        token_threshold: int = 4000,
        max_turns_per_segment: int = 50,
        session_ttl_hours: int = 24,
        
        # Other options
        streaming: bool = False,
        **kwargs
    ):
        """Initialize ChukAgent with comprehensive debugging."""
        
        # Core agent configuration
        self.name = name
        self.description = description
        self.instruction = instruction or f"You are {name}, a helpful AI assistant."
        self.provider = provider
        self.model = model
        self.use_system_prompt_generator = use_system_prompt_generator
        self.streaming = streaming
        self.enable_tools = enable_tools
        self.debug_tools = debug_tools
        
        # MCP configuration
        self.mcp_config_file = mcp_config_file
        self.mcp_servers = mcp_servers or []
        self.mcp_transport = mcp_transport
        self.mcp_sse_servers = mcp_sse_servers or []
        self.tool_namespace = tool_namespace
        self.max_concurrency = max_concurrency
        self.tool_timeout = tool_timeout
        
        # Tool components (lazy initialization)
        self.registry = None
        self.executor = None
        self.stream_manager = None
        self._tools_initialized = False
        self._tool_call_count = 0
        self._last_tool_init_time = None
        
        # Internal session management
        self.enable_sessions = enable_sessions and HAS_SESSION_SUPPORT
        if self.enable_sessions:
            self._setup_internal_sessions(
                infinite_context=infinite_context,
                token_threshold=token_threshold,
                max_turns_per_segment=max_turns_per_segment,
                session_ttl_hours=session_ttl_hours
            )
        else:
            self._ai_sessions = {}
        
        logger.debug(f"🚀 Initialized ChukAgent '{name}' with {mcp_transport} MCP transport")

    def _setup_internal_sessions(
        self, 
        infinite_context: bool,
        token_threshold: int, 
        max_turns_per_segment: int,
        session_ttl_hours: int
    ):
        """Setup agent's internal session management."""
        try:
            sandbox_id = f"chuk-agent-{self.name.lower().replace('_', '-')}"
            setup_chuk_sessions_storage(
                sandbox_id=sandbox_id,
                default_ttl_hours=session_ttl_hours
            )
            
            self.session_config = {
                "infinite_context": infinite_context,
                "token_threshold": token_threshold, 
                "max_turns_per_segment": max_turns_per_segment
            }
            
            self._ai_sessions: Dict[str, AISessionManager] = {}
            
            if self.debug_tools:
                logger.debug(f"🔧 Agent {self.name} session management enabled (sandbox: {sandbox_id})")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to setup sessions for agent {self.name}: {e}")
            self.enable_sessions = False
            self._ai_sessions = {}

    def _get_ai_session(self, session_id: Optional[str]) -> Optional[AISessionManager]:
        """Get or create AI session manager for internal session tracking."""
        if not self.enable_sessions or not session_id:
            return None
            
        if session_id not in self._ai_sessions:
            try:
                self._ai_sessions[session_id] = AISessionManager(**self.session_config)
            except Exception as e:
                logger.error(f"❌ Failed to create AI session {session_id}: {e}")
                return None
                
        return self._ai_sessions[session_id]

    def get_system_prompt(self) -> str:
        """Get system prompt, optionally using chuk_llm's generator."""
        if self.use_system_prompt_generator:
            generator = SystemPromptGenerator()
            base_prompt = generator.generate_prompt({})
            return f"{base_prompt}\n\n{self.instruction}"
        else:
            return self.instruction

    async def get_llm_client(self):
        """Get LLM client for this agent."""
        return get_client(provider=self.provider, model=self.model)

    def _extract_response_content(self, response) -> str:
        """Extract content from chuk_llm response with null safety."""
        if response is None:
            return ""
        
        if isinstance(response, dict):
            content = response.get("response", response.get("content", ""))
            return content if content is not None else ""
        elif hasattr(response, 'content'):
            return response.content or ""
        elif hasattr(response, 'response'):
            return response.response or ""
        else:
            return str(response) if response is not None else ""

    async def _safe_track_ai_response(self, ai_session, content: str, model: str, provider: str) -> None:
        """Safely track AI response with comprehensive validation."""
        if not ai_session:
            return
        
        if not content:
            if self.debug_tools:
                logger.debug("🔍 Skipping empty AI response tracking")
            return
            
        if not isinstance(content, str):
            if self.debug_tools:
                logger.debug(f"🔧 Converting non-string response to string: {type(content)}")
            content = str(content)
        
        content = content.strip()
        if not content:
            if self.debug_tools:
                logger.debug("🔍 Skipping whitespace-only AI response")
            return
        
        model = str(model) if model else "unknown"
        provider = str(provider) if provider else "unknown"
        
        try:
            await ai_session.ai_responds(content, model=model, provider=provider)
            if self.debug_tools:
                logger.debug(f"✅ Successfully tracked AI response ({len(content)} chars)")
        except Exception as e:
            logger.warning(f"⚠️ Failed to track AI response: {e}")

    async def _safe_track_user_message(self, ai_session, message: str) -> None:
        """Safely track user message with validation."""
        if not ai_session:
            return
        
        if not message:
            if self.debug_tools:
                logger.debug("🔍 Skipping empty user message tracking")
            return
            
        if not isinstance(message, str):
            if self.debug_tools:
                logger.debug(f"🔧 Converting non-string message to string: {type(message)}")
            message = str(message)
        
        message = message.strip()
        if not message:
            if self.debug_tools:
                logger.debug("🔍 Skipping whitespace-only user message")
            return
        
        try:
            await ai_session.user_says(message)
            if self.debug_tools:
                logger.debug(f"✅ Successfully tracked user message ({len(message)} chars)")
        except Exception as e:
            logger.warning(f"⚠️ Failed to track user message: {e}")

    async def initialize_tools(self):
        """Initialize MCP connection and tools with cleaner logging."""
        if self._tools_initialized or not self.enable_tools:
            if self.debug_tools:
                logger.debug(f"🔧 Skipping tool initialization - already initialized: {self._tools_initialized}, tools enabled: {self.enable_tools}")
            return
        
        init_start_time = time.time()
        logger.debug(f"🔧 Initializing tools for {self.name}...")
        
        try:
            if self.mcp_transport == "stdio" and self.mcp_servers and self.mcp_config_file:
                server_names = {i: name for i, name in enumerate(self.mcp_servers)}
                
                if self.debug_tools:
                    logger.debug(f"🔗 Setting up stdio MCP with servers: {self.mcp_servers}")
                    logger.debug(f"📄 Using config file: {self.mcp_config_file}")
                
                setup_start = time.time()
                _, self.stream_manager = await setup_mcp_stdio(
                    config_file=self.mcp_config_file,
                    servers=self.mcp_servers,
                    server_names=server_names,
                    namespace=self.tool_namespace,
                )
                setup_time = time.time() - setup_start
                
                if self.debug_tools:
                    logger.debug(f"⏱️ MCP stdio setup took {setup_time:.2f}s")
                
            elif self.mcp_transport == "sse" and self.mcp_sse_servers:
                server_names = {i: server["name"] for i, server in enumerate(self.mcp_sse_servers)}
                
                if self.debug_tools:
                    logger.debug(f"🔗 Setting up SSE MCP with servers: {[s['name'] for s in self.mcp_sse_servers]}")
                
                setup_start = time.time()
                _, self.stream_manager = await setup_mcp_sse(
                    servers=self.mcp_sse_servers,
                    server_names=server_names,
                    namespace=self.tool_namespace,
                )
                setup_time = time.time() - setup_start
                
                if self.debug_tools:
                    logger.debug(f"⏱️ MCP SSE setup took {setup_time:.2f}s")
            
            # Stream manager setup
            if self.stream_manager:
                if self.debug_tools:
                    logger.debug(f"✅ Stream manager created: {type(self.stream_manager)}")
                    if hasattr(self.stream_manager, 'server_names'):
                        logger.debug(f"🔧 Server names: {self.stream_manager.server_names}")
                
                # Get registry and executor (move timing to debug)
                registry_start = time.time()
                self.registry = await ToolRegistryProvider.get_registry()
                registry_time = time.time() - registry_start
                
                executor_start = time.time()
                strategy = InProcessStrategy(
                    self.registry,
                    default_timeout=self.tool_timeout,
                    max_concurrency=self.max_concurrency,
                )
                self.executor = ToolExecutor(self.registry, strategy=strategy)
                executor_time = time.time() - executor_start
                
                if self.debug_tools:
                    logger.debug(f"⏱️ Tool registry creation took {registry_time:.2f}s")
                    logger.debug(f"⏱️ Tool executor creation took {executor_time:.2f}s")
                
                # Test tools availability
                try:
                    test_start = time.time()
                    available_tools = await self.get_available_tools()
                    test_time = time.time() - test_start
                    
                    # Keep tool info at INFO level but clean it up
                    logger.debug(f"✅ Found {len(available_tools)} available tools: {available_tools}")
                    
                    if self.debug_tools:
                        logger.debug(f"⏱️ Tool discovery took {test_time:.2f}s")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to list available tools: {e}")
                
                # Test tool schema generation (move details to debug)
                try:
                    schema_start = time.time()
                    tool_schemas = await self.generate_tools_schema()
                    schema_time = time.time() - schema_start
                    
                    if tool_schemas:
                        logger.debug(f"✅ Generated {len(tool_schemas)} tool schemas")
                    
                    if self.debug_tools:
                        logger.debug(f"⏱️ Tool schema generation took {schema_time:.2f}s")
                        if tool_schemas:
                            for i, schema in enumerate(tool_schemas[:3]):  # Show first 3
                                tool_name = schema.get('function', {}).get('name', 'unknown')
                                logger.debug(f"🔧 Tool schema {i+1}: {tool_name}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate tool schemas: {e}")
                
                logger.debug(f"✅ MCP initialized successfully")
            else:
                logger.warning("❌ No stream manager created - tools will not be available")
            
            self._tools_initialized = True
            self._last_tool_init_time = time.time()
            
            total_time = time.time() - init_start_time
            logger.debug(f"🎉 Tool initialization completed in {total_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP: {e}")
            logger.exception("MCP initialization error:")
            self._tools_initialized = True  # Mark as initialized to prevent retry loops
            self.enable_tools = False  # Disable tools on failure

    async def get_available_tools(self) -> List[str]:
        """Get list of available tools with debugging."""
        if not self.registry or not self.enable_tools:
            if self.debug_tools:
                logger.debug(f"🔍 No tools available - registry: {self.registry is not None}, tools enabled: {self.enable_tools}")
            return []
            
        try:
            start_time = time.time()
            tools = await self.registry.list_tools()
            list_time = time.time() - start_time
            
            filtered_tools = [name for ns, name in tools if ns == self.tool_namespace]
            
            if self.debug_tools:
                logger.debug(f"🔧 Listed {len(tools)} total tools in {list_time:.2f}s")
                logger.debug(f"🔧 Filtered to {len(filtered_tools)} tools in namespace '{self.tool_namespace}'")
                logger.debug(f"🔧 Available tools: {filtered_tools}")
            
            return filtered_tools
        except Exception as e:
            logger.error(f"❌ Error getting tools: {e}")
            return []

    async def execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute tool calls with cleaner logging."""
        if not self.executor or not self.enable_tools:
            error_msg = "Tool executor not available"
            logger.error(f"❌ {error_msg}")
            return [{"error": error_msg} for _ in tool_calls]
        
        self._tool_call_count += 1
        is_first_call = self._tool_call_count == 1
        
        # Keep high-level info, move details to debug
        logger.debug(f"🔧 Executing {len(tool_calls)} tool calls")
        
        if self.debug_tools:
            logger.debug(f"🔧 TOOL EXECUTION #{self._tool_call_count} (first call: {is_first_call})")
            logger.debug(f"🔧 Tool timeout: {self.tool_timeout}s")
            logger.debug(f"🔧 Max concurrency: {self.max_concurrency}")
            logger.debug(f"🔧 Time since tool init: {time.time() - self._last_tool_init_time:.2f}s" if self._last_tool_init_time else "Never")
        
        # Convert to ToolCall objects
        calls = []
        for i, tc in enumerate(tool_calls):
            func = tc.get("function", {})
            tool_name = func.get("name", "")
            
            # Move detailed tool call info to debug
            if self.debug_tools:
                logger.debug(f"🔧 Tool call {i+1}: {tool_name}")
            
            # Remove namespace prefix if present
            if tool_name.startswith(f"{self.tool_namespace}."):
                original_name = tool_name
                tool_name = tool_name[len(f"{self.tool_namespace}."):]
                if self.debug_tools:
                    logger.debug(f"🔧 Removed namespace prefix: {original_name} -> {tool_name}")
            
            # Parse arguments
            args = func.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                    if self.debug_tools:
                        logger.debug(f"🔧 Parsed JSON arguments: {args}")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse tool arguments: {args}, error: {e}")
                    args = {}
            
            # Create ToolCall with actual arguments
            full_tool_name = f"{self.tool_namespace}.{tool_name}"
            calls.append(ToolCall(
                tool=full_tool_name,
                arguments=args
            ))
            
            if self.debug_tools:
                logger.debug(f"🔧 Created ToolCall: {full_tool_name} with args: {args}")
        
        # Execute tools with timing
        execution_start = time.time()
        if self.debug_tools:
            logger.debug(f"⏱️ Starting tool execution at {execution_start}")
        
        try:
            # Add timeout wrapper for debugging
            async def execute_with_timeout():
                try:
                    return await self.executor.execute(calls)
                except Exception as e:
                    logger.error(f"❌ Tool executor.execute() failed: {e}")
                    logger.exception("Tool execution error:")
                    raise
            
            # Execute with timeout and timing
            try:
                results = await asyncio.wait_for(
                    execute_with_timeout(),
                    timeout=self.tool_timeout + 5  # Add 5s buffer
                )
                execution_time = time.time() - execution_start
                
                # Keep summary info logging, move details to debug
                logger.debug(f"✅ Tool execution completed in {execution_time:.2f}s")
                
            except asyncio.TimeoutError:
                execution_time = time.time() - execution_start
                error_msg = f"Tool execution timed out after {execution_time:.2f}s (timeout: {self.tool_timeout}s)"
                logger.error(f"⏰ {error_msg}")
                
                # Return timeout errors for all calls
                return [{
                    "tool_call_id": tc.get("id"),
                    "content": f"Error: Timeout after {self.tool_timeout}s"
                } for tc in tool_calls]
            
            # Format results with appropriate logging levels
            formatted_results = []
            successful_count = 0
            
            for i, (tc, result) in enumerate(zip(tool_calls, results)):
                tool_name = tc.get("function", {}).get("name", "unknown")
                
                if result.error:
                    logger.warning(f"⚠️ Tool {tool_name} failed: {result.error}")
                    formatted_results.append({
                        "tool_call_id": tc.get("id"),
                        "content": f"Error: {result.error}"
                    })
                else:
                    content = result.result
                    if isinstance(content, (dict, list)):
                        content = json.dumps(content, indent=2)
                    elif content is None:
                        content = "No result"
                    
                    content_str = str(content)
                    successful_count += 1
                    
                    # Move detailed success info to debug
                    if self.debug_tools:
                        logger.debug(f"✅ Tool {tool_name} succeeded: {len(content_str)} chars")
                        logger.debug(f"🔧 Tool {tool_name} result preview: {content_str[:200]}...")
                    
                    formatted_results.append({
                        "tool_call_id": tc.get("id"), 
                        "content": content_str
                    })
            
            # Keep high-level summary at info level
            logger.debug(f"🎉 Tool execution: {successful_count}/{len(formatted_results)} successful")
            return formatted_results
            
        except Exception as e:
            execution_time = time.time() - execution_start
            error_msg = f"Tool execution failed after {execution_time:.2f}s: {str(e)}"
            logger.error(f"❌ {error_msg}")
            logger.exception("Tool execution exception:")
            return [{"error": error_msg} for _ in tool_calls]

    async def generate_tools_schema(self) -> List[Dict[str, Any]]:
        """Generate OpenAI-style tool schema with cleaner logging."""
        if not self.stream_manager or not self.enable_tools:
            if self.debug_tools:
                logger.debug(f"🔍 No schema generation - stream manager: {self.stream_manager is not None}, tools enabled: {self.enable_tools}")
            return []
        
        # Move detailed schema generation to debug
        if self.debug_tools:
            logger.debug(f"🔧 Generating tool schemas...")
        
        tools = []
        
        try:
            # Method 1: Try get_all_tools() first
            try:
                if self.debug_tools:
                    logger.debug("🔧 Trying get_all_tools()...")
                
                start_time = time.time()
                all_tools = self.stream_manager.get_all_tools()
                get_time = time.time() - start_time
                
                if self.debug_tools:
                    logger.debug(f"🔧 get_all_tools() returned {len(all_tools)} tools in {get_time:.2f}s")
                
                for i, tool_info in enumerate(all_tools):
                    tool_name = tool_info.get('name', '')
                    description = tool_info.get('description', f"Execute {tool_name} tool")
                    input_schema = tool_info.get('inputSchema', {})
                    
                    if self.debug_tools:
                        logger.debug(f"🔧 Tool {i+1}: {tool_name} - {description[:50]}...")
                    
                    if tool_name:
                        openai_tool = {
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "description": description,
                                "parameters": input_schema
                            }
                        }
                        tools.append(openai_tool)
                        if self.debug_tools:
                            logger.debug(f"✅ Added tool schema for {tool_name}")
                
                if tools:
                    # Keep high-level info
                    logger.debug(f"✅ Generated {len(tools)} tool schemas")
                    return tools
                    
            except Exception as e:
                if self.debug_tools:
                    logger.debug(f"⚠️ get_all_tools() failed: {e}")
            
            # Method 2: Fallback to list_tools() with server names
            server_names = getattr(self.stream_manager, 'server_names', {})
            if self.debug_tools:
                logger.debug(f"🔧 Fallback: trying list_tools() with server names: {server_names}")
            
            for server_id, server_name in server_names.items():
                try:
                    if self.debug_tools:
                        logger.debug(f"🔧 Listing tools for server: {server_name}")
                    
                    start_time = time.time()
                    server_tools = await self.stream_manager.list_tools(server_name)
                    list_time = time.time() - start_time
                    
                    if self.debug_tools:
                        logger.debug(f"🔧 list_tools({server_name}) returned {len(server_tools)} tools in {list_time:.2f}s")
                    
                    for tool_info in server_tools:
                        tool_name = tool_info.get('name', '')
                        description = tool_info.get('description', f"Execute {tool_name} tool")
                        input_schema = tool_info.get('inputSchema', {})
                        
                        if tool_name:
                            openai_tool = {
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "description": description,
                                    "parameters": input_schema
                                }
                            }
                            tools.append(openai_tool)
                            if self.debug_tools:
                                logger.debug(f"✅ Added tool schema for {tool_name}")
                
                except Exception as e:
                    logger.error(f"❌ list_tools({server_name}) failed: {e}")
            
            if tools:
                logger.debug(f"✅ Generated {len(tools)} tool schemas")
                return tools
            else:
                logger.warning("⚠️ No tools generated from stream manager")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error generating tool schemas from stream manager: {e}")
            logger.exception("Tool schema generation error:")
            return []

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        use_tools: bool = True,
        session_id: Optional[str] = None,
        **llm_kwargs
    ) -> Dict[str, Any]:
        """Complete a conversation with minimal key logging."""
        if self.debug_tools:
            logger.debug(f"🔧 Starting completion - use_tools: {use_tools}, session_id: {session_id}")
        
        # Always initialize tools if they're enabled
        if self.enable_tools:
            await self.initialize_tools()
        
        # Session handling (abbreviated for space)
        ai_session = self._get_ai_session(session_id) if session_id else None
        if ai_session:
            try:
                context = await ai_session.get_conversation()
                if context:
                    system_msg = messages[0] if messages and messages[0]["role"] == "system" else None
                    user_messages = messages[1:] if system_msg else messages
                    
                    enhanced_messages = []
                    if system_msg:
                        enhanced_messages.append(system_msg)
                    enhanced_messages.extend(context[-5:])
                    enhanced_messages.extend(user_messages)
                    messages = enhanced_messages
            except Exception as e:
                logger.warning(f"⚠️ Failed to get session context: {e}")
        
        llm_client = await self.get_llm_client()
        
        # Get tools if requested and available
        tools = None
        if use_tools and self.enable_tools:
            schema_start = time.time()
            tools = await self.generate_tools_schema()
            schema_time = time.time() - schema_start
            
            if tools:
                if self.debug_tools:
                    logger.debug(f"🔧 Using {len(tools)} tools (schema generation: {schema_time:.2f}s)")
            else:
                logger.warning("⚠️ No tools available, proceeding without tools")
                use_tools = False
        
        # Track user message in session
        if ai_session:
            user_message = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break
            if user_message:
                await self._safe_track_user_message(ai_session, user_message)
        
        # Call LLM
        try:
            if use_tools and tools:
                llm_start = time.time()
                response = await llm_client.create_completion(
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    **llm_kwargs
                )
                llm_time = time.time() - llm_start
                
                if self.debug_tools:
                    logger.debug(f"⏱️ LLM completion took {llm_time:.2f}s")
                
                # Handle tool calls
                tool_calls = None
                content = None
                
                if isinstance(response, dict):
                    tool_calls = response.get('tool_calls', [])
                    content = response.get('response') or response.get('content')
                else:
                    tool_calls = getattr(response, 'tool_calls', [])
                    content = getattr(response, 'content', None)
                
                if tool_calls:
                    # ✅ KEY INFO LOG: Tool usage
                    logger.info(f"🔧 {self.name} using {len(tool_calls)} tools")
                    
                    if self.debug_tools:
                        for i, tc in enumerate(tool_calls):
                            tool_name = tc.get("function", {}).get("name", "unknown")
                            logger.debug(f"🔧 Tool call {i+1}: {tool_name}")
                    
                    # Execute tools
                    tool_results = await self.execute_tools(tool_calls)
                    
                    # Add tool results to conversation and get final response
                    enhanced_messages = messages + [
                        {
                            "role": "assistant",
                            "content": content or "I'll use my tools to help you.",
                            "tool_calls": tool_calls
                        }
                    ]
                    
                    for result in tool_results:
                        enhanced_messages.append({
                            "role": "tool",
                            "tool_call_id": result.get("tool_call_id", "unknown"),
                            "content": result.get("content", "No result")
                        })
                    
                    # Get final response
                    final_start = time.time()
                    final_response = await llm_client.create_completion(messages=enhanced_messages, **llm_kwargs)
                    final_time = time.time() - final_start
                    
                    if self.debug_tools:
                        logger.debug(f"⏱️ Final LLM completion took {final_time:.2f}s")
                    
                    final_content = self._extract_response_content(final_response)
                    
                    await self._safe_track_ai_response(ai_session, final_content, self.model, self.provider)
                    
                    # ✅ KEY INFO LOG: Completion success
                    logger.info(f"✅ {self.name} completed with tools")
                    
                    return {
                        "content": final_content,
                        "tool_calls": tool_calls,
                        "tool_results": tool_results,
                        "usage": getattr(final_response, 'usage', None) if hasattr(final_response, 'usage') else response.get('usage')
                    }
                else:
                    if self.debug_tools:
                        logger.debug("🔧 No tool calls requested by LLM")
                    final_content = content or self._extract_response_content(response)
                    
                    await self._safe_track_ai_response(ai_session, final_content, self.model, self.provider)
                    
                    # ✅ KEY INFO LOG: Completion success (no tools)
                    logger.info(f"✅ {self.name} completed without tools")
                    
                    return {
                        "content": final_content,
                        "tool_calls": [],
                        "tool_results": [],
                        "usage": getattr(response, 'usage', None) if hasattr(response, 'usage') else response.get('usage')
                    }
            else:
                # No tools, simple completion
                if self.debug_tools:
                    logger.debug("🔧 Proceeding with simple completion (no tools)")
                    
                response = await llm_client.create_completion(messages=messages, **llm_kwargs)
                final_content = self._extract_response_content(response)
                
                await self._safe_track_ai_response(ai_session, final_content, self.model, self.provider)
                
                # ✅ KEY INFO LOG: Simple completion success
                logger.info(f"✅ {self.name} completed (no tools available)")
                
                return {
                    "content": final_content,
                    "tool_calls": [],
                    "tool_results": [],
                    "usage": getattr(response, 'usage', None) if hasattr(response, 'usage') else response.get('usage')
                }
        except Exception as e:
            logger.error(f"❌ Error in LLM completion: {e}")
            logger.exception("LLM completion error:")
            raise

    async def chat(self, user_message: str, session_id: Optional[str] = None, **kwargs) -> str:
        """Simple chat interface with session support."""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message}
        ]
        
        result = await self.complete(messages, session_id=session_id, **kwargs)
        return result["content"] or "No response generated"

    async def get_conversation_history(self, session_id: Optional[str] = None) -> List[Dict[str, str]]:
        """Get conversation history for a session."""
        ai_session = self._get_ai_session(session_id) if session_id else None
        if not ai_session:
            return []
            
        try:
            return await ai_session.get_conversation()
        except Exception as e:
            logger.error(f"❌ Failed to get conversation history: {e}")
            return []

    async def get_session_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get session statistics."""
        ai_session = self._get_ai_session(session_id) if session_id else None
        if not ai_session:
            return {"total_tokens": 0, "estimated_cost": 0}
            
        try:
            return ai_session.get_stats()
        except Exception as e:
            logger.error(f"❌ Failed to get session stats: {e}")
            return {"total_tokens": 0, "estimated_cost": 0}

    async def shutdown(self):
        """Cleanup MCP connections."""
        if self.stream_manager:
            try:
                await self.stream_manager.close()
                logger.debug(f"🔌 Closed MCP stream manager for {self.name}")
            except Exception as e:
                logger.warning(f"⚠️ Error closing stream manager: {e}")


# Export the main class
__all__ = ["ChukAgent"]