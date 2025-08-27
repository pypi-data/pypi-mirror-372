"""
Dynamic tool creation for MCP Rules Server
"""

import logging
from typing import Callable, Dict, List

from mcp.server.fastmcp import FastMCP

from .models import ToolInfo
from .rule_manager import RuleManager


logger = logging.getLogger(__name__)


class ToolFactory:
    """Factory for creating and managing dynamic MCP tools."""
    
    def __init__(self, rule_manager: RuleManager, mcp_server: FastMCP):
        """Initialize the tool factory."""
        self.rule_manager = rule_manager
        self.mcp_server = mcp_server
        self._registered_tools: Dict[str, ToolInfo] = {}
        
        logger.info("Initialized ToolFactory")
    
    def register_all_tools(self) -> None:
        """Register all available tools with the MCP server."""
        # Clear existing tools
        self._registered_tools.clear()
        
        # Register only the two main tools like Context7
        self._register_main_tools()
        
        logger.info(f"Registered {len(self._registered_tools)} tools")
    
    def _register_main_tools(self) -> None:
        """Register the two main tools like Context7."""
        
        @self.mcp_server.tool()
        def get_rules(domain: str) -> str:
            """Get rules and best practices for a specific domain."""
            if not self.rule_manager.has_domain(domain):
                available_domains = self.rule_manager.get_available_domains()
                return f"""Error: Domain '{domain}' not found.

Available domains: {', '.join(available_domains)}

Use list_rules() to see all available rule domains."""
            
            content = self.rule_manager.get_rule_content(domain)
            if content:
                logger.debug(f"Retrieved rules for domain: {domain}")
                return content
            else:
                return f"Error: No content found for domain '{domain}'"
        
        @self.mcp_server.tool()
        def list_rules() -> str:
            """List all available rule domains with descriptions."""
            domains = self.rule_manager.get_available_domains()
            
            if not domains:
                return "No rule domains available. Please add markdown files to the rules/ directory."
            
            result = "# Available Rule Domains\n\n"
            
            for domain in domains:
                metadata = self.rule_manager.get_rule_metadata(domain)
                if metadata:
                    result += f"## {domain}\n"
                    result += f"**Description:** {metadata.description}\n"
                    result += f"**Version:** {metadata.version}\n"
                    result += f"**Last Updated:** {metadata.last_updated}\n\n"
                    result += f"To get these rules, use: `get_rules('{domain}')`\n\n"
                else:
                    result += f"## {domain}\n"
                    result += f"Rules available for this domain.\n"
                    result += f"To get these rules, use: `get_rules('{domain}')`\n\n"
            
            logger.debug(f"Listed {len(domains)} rule domains")
            return result
        
        # Track the two main tools
        main_tools = [
            ToolInfo("get_rules", "Get rules and best practices for a specific domain", "main"),
            ToolInfo("list_rules", "List all available rule domains with descriptions", "main")
        ]
        
        for tool_info in main_tools:
            self._registered_tools[tool_info.name] = tool_info
        
        logger.debug("Registered main tools: get_rules, list_rules")
    

    
    def get_registered_tools(self) -> Dict[str, ToolInfo]:
        """Get information about all registered tools."""
        return self._registered_tools.copy()
    
    def is_tool_registered(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._registered_tools
    
    def get_tool_info(self, tool_name: str) -> ToolInfo:
        """Get information about a specific tool."""
        return self._registered_tools.get(tool_name)