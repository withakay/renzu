"""MCP tool registrations."""

from app.mcp.tools.glass import register_glass_tools
from app.mcp.tools.retrieval import register_retrieval_tools

__all__ = ["register_glass_tools", "register_retrieval_tools"]
