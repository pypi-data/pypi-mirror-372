"""
A Model Context Protocol (MCP) server of Stash that enables AI assistants to interact 
"""

__version__ = "1.2.0"
__author__ = "Stash Team"
__email__ = "ayberk@usestash.com"
__description__ = "A Model Context Protocol (MCP) server for Stash issue analysis."

from .main import main

__all__ = ["main", "__version__"]
