"""MCP server for 360 Research embedding services."""

import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    Tool,
)

from .tools import EmbeddingTools
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EmbeddingMCPServer:
    """MCP server for 360 Research embedding services."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("embedding-mcp-server")
        self.embedding_tools = EmbeddingTools()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Handle list tools request."""
            tools = self.embedding_tools.get_tools()
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool call request."""
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
            if name == "text_embedding":
                return await self.embedding_tools.call_text_embedding(arguments)
            elif name == "image_embedding":
                return await self.embedding_tools.call_image_embedding(arguments)
            elif name == "embedding":
                return await self.embedding_tools.call_embedding(arguments)
            else:
                error_result = {"success": False, "embedding": None, "error_msg": f"Unknown tool: {name}"}
                return error_result


async def run_stdio_server():
    """Run the MCP server using stdio transport."""
    try:
        server = EmbeddingMCPServer()
        
        # Initialize the server
        init_options = InitializationOptions(
            server_name="embedding-mcp-server",
            server_version="0.1.2",
            capabilities={
                "tools": {}
            }
        )
        
        logger.info("Starting stdio MCP server...")
        async with stdio_server() as (read, write):
            logger.info("Stdio transport established, running server...")
            await server.server.run(
                read,
                write,
                init_options
            )
    except Exception as e:
        logger.error(f"Error in stdio server: {e}")
        raise

