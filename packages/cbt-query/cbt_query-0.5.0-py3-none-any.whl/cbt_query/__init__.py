"""
CBT Query MCP Server Package

A simple Model Context Protocol (MCP) server for querying TensorRT test coverage and case mapping.
"""

__version__ = "0.5.0"
__author__ = "CBT Team"
__description__ = "Simple CBT query MCP Server"

# package imports
from .server import fetch_json, format_list_param

__all__ = [
    "fetch_json",
    "format_list_param",
    "__version__",
    "__author__",
    "__description__"
]
