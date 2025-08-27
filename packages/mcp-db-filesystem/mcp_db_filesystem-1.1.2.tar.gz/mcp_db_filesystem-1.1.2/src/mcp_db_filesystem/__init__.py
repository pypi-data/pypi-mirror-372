"""
MCP Database Filesystem
=======================

A simple and efficient MCP server for database access and filesystem operations.

Features:
- Database operations (queries, commands, schema inspection)
- Filesystem operations (read, write, directory listing)
- Security features (SQL injection protection, filesystem access control)
- Environment variable configuration
- Cross-platform support

Author: PJ
Email: peng.it@qq.com
License: MIT
"""

__version__ = "1.1.2"
__author__ = "PJ"
__email__ = "peng.it@qq.com"
__license__ = "MIT"

# 导出主要组件
from .server import main

__all__ = ["main", "__version__", "__author__", "__email__", "__license__"]
