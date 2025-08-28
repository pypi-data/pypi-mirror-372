import anyio
import logging
from typing import Any, List, Union
import mcp.types as types
from mcp.server.lowlevel import Server

# Handle SSE transport directly without using asyncio.run()
import uvicorn
from uvicorn.config import Config

# Create Starlette app synchronously
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from mcp.server.stdio import stdio_server

from alita_mcp.utils.name import build_agent_identifier

logger = logging.getLogger(__name__)

def create_server(agent: Union[Any, List[Any]], name=None):
    """Create and return an MCP server instance.
    
    Args:
        agent: Single agent or list of agents to serve
        name: Optional server name (defaults to agent name for single agents)
    """
    # Use agent name as server name if not specified and if agent has a name
    if name is None:
        if not isinstance(agent, list) and hasattr(agent, 'agent_name'):
            name = agent.agent_name
        else:
            name = "mcp-simple-prompt"
    
    app = Server(name)
    
    # Convert single agent to a list for uniform handling
    agents = agent if isinstance(agent, list) else [agent]
    
    # Create a dictionary of available agents by name
    available_agents = {}
    for a in agents:
        if hasattr(a, 'agent_name'):
            identifier = build_agent_identifier(a.agent_name)
            if identifier in available_agents:
                logger.warning(
                    "Skipping agent with colliding name: %s -> %s",
                    a.agent_name, identifier,
                )
                continue
            available_agents[identifier] = a
        else:
            # Fallback for agents without a name (assign index-based name)
            agent_index = len(available_agents)
            available_agents[f"agent_{agent_index}"] = a
    
    @app.call_tool()
    async def fetch_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name not in available_agents:
            raise ValueError(f"Tool '{name}' not found")
        if "user_input" not in arguments:
            raise ValueError("Missing required argument 'user_input'")
            
        # Get the correct agent by name
        current_agent = available_agents[name]
        response = current_agent.predict(**arguments)
        print(response)
        if response.get('chat_history') and isinstance(response['chat_history'], list):
            return [types.TextContent(type="text", text=response['chat_history'][-1].get('content'))]
        return [types.TextContent(type="text", text="No messages found in response")]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        tools = []
        for agent_name, agent_obj in available_agents.items():
            # Get description and schema safely
            description = getattr(agent_obj, 'description', f"Agent {agent_name}")
            
            # Handle agents that might not have pydantic_model attribute
            if hasattr(agent_obj, 'pydantic_model') and hasattr(agent_obj.pydantic_model, 'schema'):
                schema = agent_obj.pydantic_model.schema()
            else:
                schema = {"title": agent_name, "type": "object", "properties": {"user_input": {"type": "string"}}}
            
            tools.append(
                types.Tool(
                    name=agent_name,
                    description=description,
                    inputSchema=schema
                )
            )
        return tools
        
    return app


def run(agent: Any, server=None, transport="stdio", host='0.0.0.0', port=8000):
    """Run the MCP server.
    
    Args:
        agent: The agent or list of agents to serve
        server: Optional pre-configured server (will create one if not provided)
        transport: Transport mechanism ('stdio' or 'sse')
        host: Host to bind to when using SSE transport
        port: Port to listen on when using SSE transport
    """
    # Create server if not provided
    if server is None:
        # Get agent name if available
        name = agent.agent_name if hasattr(agent, 'agent_name') else None
        app = create_server(agent, name)
    else:
        app = server
    
    if transport.lower() == "sse":
        # Set up SSE transport
        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )
        
        # Run with uvicorn directly
        config = Config(
            app=starlette_app,
            host=host,
            port=port,
            timeout_graceful_shutdown=5,
        )
        
        logger.debug(f"Starting MCP server with SSE transport on {host}:{port}")
        server = uvicorn.Server(config)
        server.run()
    elif transport.lower() == "stdio":
        logger.debug("Starting MCP server with stdio transport")
        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
        anyio.run(arun)
    else:
        raise ValueError(f"Unsupported transport: {transport}")