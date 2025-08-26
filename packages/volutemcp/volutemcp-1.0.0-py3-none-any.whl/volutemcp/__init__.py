"""
VoluteMCP - PowerPoint Integration for AI Applications

A Model Context Protocol (MCP) server that enables AI agents to interact with
Microsoft PowerPoint presentations and local files on Windows machines.

Features:
- PowerPoint COM automation
- Comprehensive metadata extraction
- Local file system access
- Hybrid cloud/local architecture
- FastMCP-based implementation

Example Usage:
    # Install via pip
    pip install volutemcp
    
    # Run local server for PowerPoint integration
    volutemcp-local
    
    # Use in MCP configuration
    {
        "volutemcp-local": {
            "command": "volutemcp-local",
            "args": ["--transport", "stdio"],
            "env": {}
        }
    }
"""

__version__ = "1.0.0"
__author__ = "Coritan"
__email__ = "your-email@example.com"
__description__ = "MCP server for PowerPoint integration in AI applications"

from .server import main as server_main
from .server_local import main as local_main

__all__ = ["server_main", "local_main"]
