from typing import Dict, Any, Optional
import aiohttp
import json
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MCPTools:
    """MCP (Model Context Protocol) tools for external services."""
    
    def __init__(self, server_url: str = None):
        self.server_url = server_url or settings.MCP_SERVER_URL
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call an MCP tool."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "tool": tool_name,
                    "arguments": arguments
                }
                
                async with session.post(
                    f"{self.server_url}/call",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"MCP call failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"MCP tool error: {e}")
            return None
    
    async def get_project_management_tools(self) -> Optional[Dict[str, Any]]:
        """Get project management integration tools."""
        return await self.call_mcp_tool("get_project_tools", {})
    
    async def get_documentation_tools(self) -> Optional[Dict[str, Any]]:
        """Get documentation generation tools."""
        return await self.call_mcp_tool("get_doc_tools", {})
    
    async def get_collaboration_tools(self) -> Optional[Dict[str, Any]]:
        """Get collaboration platform tools."""
        return await self.call_mcp_tool("get_collab_tools", {})
    
    async def generate_prd_document(self, prd_data: Dict[str, Any]) -> Optional[str]:
        """Generate formatted PRD document using MCP."""
        result = await self.call_mcp_tool("generate_prd", {
            "data": prd_data,
            "format": "markdown"
        })
        return result.get("document") if result else None

mcp_tools = MCPTools()