"""MCP Server for Database and Filesystem Access."""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence
import json

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    ServerCapabilities,
    ToolsCapability
)

from .config import config
from .database import db_manager, SQLSecurityError, DatabaseConnectionError
from .mysql import mysql_manager, MySQLSecurityError, MySQLConnectionError
from .redis_manager import redis_manager, RedisConnectionError
from .filesystem import fs_manager, FilesystemSecurityError, FilesystemOperationError
from . import __version__

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.server.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        *([logging.FileHandler(config.server.log_file)] if config.server.log_file else [])
    ]
)

logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("mcp-db-filesystem")


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources."""
    resources = [
        Resource(
            uri="config://database",
            name="Database Configuration",
            description="Current database configuration settings",
            mimeType="application/json",
        ),
        Resource(
            uri="config://filesystem",
            name="Filesystem Configuration", 
            description="Current filesystem configuration settings",
            mimeType="application/json",
        ),
        Resource(
            uri="status://database",
            name="Database Status",
            description="Current database connection status",
            mimeType="application/json",
        ),
    ]
    
    return resources


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource."""
    if uri == "config://database":
        return json.dumps({
            "server": config.database.server,
            "database": config.database.database,
            "port": config.database.port,
            "use_windows_auth": config.database.use_windows_auth,
            "connection_timeout": config.database.connection_timeout,
            "command_timeout": config.database.command_timeout,
            "pool_size": config.database.pool_size,
        }, indent=2)
    
    elif uri == "config://filesystem":
        return json.dumps({
            "allowed_paths": config.filesystem.allowed_paths,
            "blocked_paths": config.filesystem.blocked_paths,
            "max_file_size": config.filesystem.max_file_size,
            "allowed_extensions": list(config.filesystem.allowed_extensions),
            "blocked_extensions": list(config.filesystem.blocked_extensions),
            "enable_write": config.filesystem.enable_write,
            "enable_delete": config.filesystem.enable_delete,
        }, indent=2)
    
    elif uri == "status://database":
        try:
            is_connected = db_manager.test_connection()
            return json.dumps({
                "connected": is_connected,
                "status": "Connected" if is_connected else "Disconnected",
                "timestamp": asyncio.get_event_loop().time(),
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "connected": False,
                "status": f"Error: {str(e)}",
                "timestamp": asyncio.get_event_loop().time(),
            }, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    tools = []

    # Add SQL Server tools only if database is available
    if db_manager.is_available():
        tools.extend([
            # SQL Server tools
            Tool(
            name="sql_query",
            description="Execute SQL SELECT query and return results",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Query parameters (optional)",
                        "additionalProperties": True
                    },

                },
                "required": ["query"]
            }
        ),
        Tool(
            name="sql_execute",
            description="Execute SQL INSERT/UPDATE/DELETE query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Query parameters (optional)",
                        "additionalProperties": True
                    },

                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_table_schema",
            description="Get table schema information",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "schema_name": {
                        "type": "string",
                        "description": "Schema name (default: dbo)",
                        "default": "dbo"
                    },

                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in database",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_name": {
                        "type": "string",
                        "description": "Schema name (default: dbo)",
                        "default": "dbo"
                    },

                }
            }
        )])

    # Add MySQL tools only if MySQL is available
    if mysql_manager.is_available():
        tools.extend([
            # MySQL tools
            Tool(
                name="mysql_query",
                description="Execute MySQL SELECT query and return results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "MySQL SELECT query to execute"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Query parameters (optional)",
                            "additionalProperties": True
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="mysql_execute",
                description="Execute MySQL INSERT/UPDATE/DELETE query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "MySQL query to execute"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Query parameters (optional)",
                            "additionalProperties": True
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Confirm dangerous operations",
                            "default": False
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="mysql_get_table_schema",
                description="Get MySQL table schema information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "database_name": {
                            "type": "string",
                            "description": "Database name (optional, uses default if not specified)"
                        }
                    },
                    "required": ["table_name"]
                }
            ),
            Tool(
                name="mysql_list_tables",
                description="List all tables in MySQL database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_name": {
                            "type": "string",
                            "description": "Database name (optional, uses default if not specified)"
                        }
                    }
                }
            ),
        ])

    # Add Redis tools only if Redis is available
    if redis_manager.is_available():
        tools.extend([
            # Redis tools
            Tool(
                name="redis_get",
                description="Get value from Redis by key",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Redis key"
                        }
                    },
                    "required": ["key"]
                }
            ),
            Tool(
                name="redis_set",
                description="Set key-value pair in Redis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Redis key"
                        },
                        "value": {
                            "type": "string",
                            "description": "Value to set"
                        },
                        "ex": {
                            "type": "integer",
                            "description": "Expiration time in seconds (optional)"
                        }
                    },
                    "required": ["key", "value"]
                }
            ),
            Tool(
                name="redis_delete",
                description="Delete keys from Redis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of keys to delete"
                        }
                    },
                    "required": ["keys"]
                }
            ),
            Tool(
                name="redis_keys",
                description="Get Redis keys matching pattern",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Key pattern (default: *)",
                            "default": "*"
                        }
                    }
                }
            ),
            Tool(
                name="redis_info",
                description="Get Redis server information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "section": {
                            "type": "string",
                            "description": "Info section (optional)"
                        }
                    }
                }
            ),
        ])

    # Always add database management tools
    tools.extend([
        # Database management tools
        Tool(
            name="database_reconnect",
            description="Attempt to reconnect to SQL Server database",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="database_status",
            description="Check all database connections status",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="mysql_reconnect",
            description="Attempt to reconnect to MySQL database",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="redis_reconnect",
            description="Attempt to reconnect to Redis",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
    ])

    # Always add filesystem tools (they don't depend on database)
    tools.extend([
        # Filesystem tools
        Tool(
            name="read_file",
            description="Read file content",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    },

                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to file"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    },
                    "create_dirs": {
                        "type": "boolean",
                        "description": "Create parent directories if needed",
                        "default": True
                    },

                },
                "required": ["file_path", "content"]
            }
        ),
        Tool(
            name="list_directory",
            description="List directory contents",
            inputSchema={
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "Path to the directory to list"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "List recursively",
                        "default": False
                    },

                },
                "required": ["dir_path"]
            }
        ),
        Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirm file deletion",
                        "default": False
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="create_directory",
            description="Create a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "Path to the directory to create"
                    },
                    "parents": {
                        "type": "boolean",
                        "description": "Create parent directories if they don't exist",
                        "default": True
                    }
                },
                "required": ["dir_path"]
            }
        ),
    ])

    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        # SQL Server tools - check availability first
        if name in ["sql_query", "sql_execute", "get_table_schema", "list_tables"]:
            if not db_manager.is_available():
                error_msg = f"❌ SQL Server工具不可用: {db_manager.get_connection_error()}"
                return [TextContent(type="text", text=error_msg)]

        # MySQL tools - check availability first
        if name in ["mysql_query", "mysql_execute", "mysql_get_table_schema", "mysql_list_tables"]:
            if not mysql_manager.is_available():
                error_msg = f"❌ MySQL工具不可用: {mysql_manager.get_connection_error()}"
                return [TextContent(type="text", text=error_msg)]

        # Redis tools - check availability first
        if name in ["redis_get", "redis_set", "redis_delete", "redis_keys", "redis_info"]:
            if not redis_manager.is_available():
                error_msg = f"❌ Redis工具不可用: {redis_manager.get_connection_error()}"
                return [TextContent(type="text", text=error_msg)]

        if name == "sql_query":
            return await handle_sql_query(arguments)
        elif name == "sql_execute":
            return await handle_sql_execute(arguments)
        elif name == "get_table_schema":
            return await handle_get_table_schema(arguments)
        elif name == "list_tables":
            return await handle_list_tables(arguments)
        elif name == "mysql_query":
            return await handle_mysql_query(arguments)
        elif name == "mysql_execute":
            return await handle_mysql_execute(arguments)
        elif name == "mysql_get_table_schema":
            return await handle_mysql_get_table_schema(arguments)
        elif name == "mysql_list_tables":
            return await handle_mysql_list_tables(arguments)
        elif name == "redis_get":
            return await handle_redis_get(arguments)
        elif name == "redis_set":
            return await handle_redis_set(arguments)
        elif name == "redis_delete":
            return await handle_redis_delete(arguments)
        elif name == "redis_keys":
            return await handle_redis_keys(arguments)
        elif name == "redis_info":
            return await handle_redis_info(arguments)
        elif name == "database_reconnect":
            return await handle_database_reconnect(arguments)
        elif name == "database_status":
            return await handle_database_status(arguments)
        elif name == "mysql_reconnect":
            return await handle_mysql_reconnect(arguments)
        elif name == "redis_reconnect":
            return await handle_redis_reconnect(arguments)
        elif name == "read_file":
            return await handle_read_file(arguments)
        elif name == "write_file":
            return await handle_write_file(arguments)
        elif name == "list_directory":
            return await handle_list_directory(arguments)
        elif name == "delete_file":
            return await handle_delete_file(arguments)
        elif name == "create_directory":
            return await handle_create_directory(arguments)

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Tool handler functions
async def handle_sql_query(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle SQL query execution."""
    query = arguments.get("query", "")
    parameters = arguments.get("parameters", {})

    try:
        result_data = db_manager.execute_query(query, parameters)

        # Extract rows from the result dictionary
        rows = result_data.get('rows', [])
        columns = result_data.get('columns', [])
        row_count = result_data.get('row_count', 0)

        # Format results for display
        if row_count == 0:
            response_text = "Query executed successfully. No results returned."
        else:
            # Create a formatted table
            if row_count == 1:
                response_text = f"Query returned 1 row:\n\n"
            else:
                response_text = f"Query returned {row_count} rows:\n\n"

            # Add column headers
            if columns:
                response_text += " | ".join(columns) + "\n"
                response_text += "-" * (len(" | ".join(columns))) + "\n"

                # Add data rows (limit to first 100 rows for display)
                display_rows = rows[:100]
                for row in display_rows:
                    row_values = [str(row.get(col, "")) for col in columns]
                    response_text += " | ".join(row_values) + "\n"

                if row_count > 100:
                    response_text += f"\n... and {row_count - 100} more rows"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"SQL query failed: {str(e)}"
        error_type = type(e).__name__
        detailed_error = f"SQL query failed: [{error_type}] {str(e)}"

        # 提供更详细的错误信息
        if "login failed" in str(e).lower():
            detailed_error += "\n💡 建议：检查数据库用户名和密码"
        elif "cannot open database" in str(e).lower():
            detailed_error += "\n💡 建议：检查数据库名称是否正确，或尝试使用 'master' 数据库"
        elif "permission" in str(e).lower() or "access denied" in str(e).lower():
            detailed_error += "\n💡 建议：检查数据库用户是否有SELECT权限"
        elif str(e) == "0" or str(e) == "":
            detailed_error = f"SQL query failed: 未知错误 (可能是连接或权限问题)\n💡 建议：检查数据库连接配置和用户权限"

        logger.error(detailed_error)
        return [TextContent(type="text", text=detailed_error)]


async def handle_sql_execute(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle SQL execution (INSERT, UPDATE, DELETE)."""
    query = arguments.get("query", "")
    parameters = arguments.get("parameters", {})
    confirm = arguments.get("confirm", False)

    try:
        # Check if confirmation is required for dangerous operations
        dangerous_keywords = ["DELETE", "DROP", "TRUNCATE", "ALTER"]
        query_upper = query.upper().strip()

        is_dangerous = any(keyword in query_upper for keyword in dangerous_keywords)

        if is_dangerous and not confirm:
            return [TextContent(
                type="text",
                text=f"This operation requires confirmation. Please add 'confirm': true to execute: {query}"
            )]

        affected_rows = db_manager.execute_non_query(query, parameters)

        response_text = f"SQL executed successfully. {affected_rows} rows affected."

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"SQL execution failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_get_table_schema(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle table schema retrieval."""
    table_name = arguments.get("table_name", "")
    schema_name = arguments.get("schema_name", "dbo")

    try:
        schema_data = db_manager.get_table_schema(table_name, schema_name)

        # Extract columns from the schema data
        columns = schema_data.get('columns', []) if isinstance(schema_data, dict) else []

        if not columns:
            response_text = f"Table '{schema_name}.{table_name}' not found or has no columns."
        else:
            response_text = f"Schema for table '{schema_name}.{table_name}':\n\n"
            response_text += "Column Name | Data Type | Nullable | Default | Key | Description\n"
            response_text += "-" * 80 + "\n"

            for col in columns:
                # Handle different column name formats (uppercase from SQL Server)
                column_name = col.get('COLUMN_NAME') or col.get('column_name', '')
                data_type = col.get('DATA_TYPE') or col.get('data_type', '')
                is_nullable = col.get('IS_NULLABLE') or col.get('is_nullable', 'YES')
                column_default = col.get('COLUMN_DEFAULT') or col.get('column_default', '')
                is_primary_key = col.get('IS_PRIMARY_KEY') or col.get('is_primary_key', 0)
                column_description = col.get('COLUMN_DESCRIPTION') or col.get('column_description', '')

                nullable = "YES" if is_nullable == 'YES' or is_nullable == True else "NO"
                default = str(column_default) if column_default else ""
                key_type = "PK" if is_primary_key else ""
                description = str(column_description) if column_description else ""

                response_text += f"{column_name} | {data_type} | {nullable} | {default} | {key_type} | {description}\n"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to get table schema: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_list_tables(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle database tables listing."""
    schema_name = arguments.get("schema_name", "dbo")

    try:
        tables = db_manager.get_database_tables(schema_name)

        if not tables:
            response_text = f"No tables found in schema '{schema_name}'."
        else:
            response_text = f"Tables in schema '{schema_name}' ({len(tables)} found):\n\n"
            for i, table in enumerate(tables, 1):
                response_text += f"{i}. {table}\n"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to list tables: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


# MySQL handler functions
async def handle_mysql_query(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MySQL query execution."""
    query = arguments.get("query", "")
    parameters = arguments.get("parameters", {})

    try:
        result_data = mysql_manager.execute_query(query, parameters)
        rows = result_data.get('rows', [])
        columns = result_data.get('columns', [])
        row_count = result_data.get('row_count', 0)

        if row_count == 0:
            response_text = "MySQL query executed successfully. No results returned."
        else:
            response_text = f"MySQL query returned {row_count} rows:\n\n"
            if columns:
                response_text += " | ".join(columns) + "\n"
                response_text += "-" * (len(" | ".join(columns))) + "\n"
                display_rows = rows[:100]
                for row in display_rows:
                    row_values = [str(row.get(col, "")) for col in columns]
                    response_text += " | ".join(row_values) + "\n"
                if row_count > 100:
                    response_text += f"\n... and {row_count - 100} more rows"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"MySQL query failed: [{type(e).__name__}] {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_mysql_execute(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MySQL execution (INSERT, UPDATE, DELETE)."""
    query = arguments.get("query", "")
    parameters = arguments.get("parameters", {})
    confirm = arguments.get("confirm", False)

    try:
        dangerous_keywords = ["DELETE", "DROP", "TRUNCATE", "ALTER"]
        query_upper = query.upper().strip()
        is_dangerous = any(keyword in query_upper for keyword in dangerous_keywords)

        if is_dangerous and not confirm:
            return [TextContent(
                type="text",
                text=f"This MySQL operation requires confirmation. Please add 'confirm': true to execute: {query}"
            )]

        affected_rows = mysql_manager.execute_non_query(query, parameters)
        response_text = f"MySQL executed successfully. {affected_rows} rows affected."
        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"MySQL execution failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_mysql_get_table_schema(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MySQL table schema retrieval."""
    table_name = arguments.get("table_name", "")
    database_name = arguments.get("database_name")

    try:
        schema_info = mysql_manager.get_table_schema(table_name, database_name)
        response_text = f"MySQL Table Schema: {schema_info['database_name']}.{schema_info['table_name']}\n\n"
        response_text += "Column Name | Data Type | Nullable | Default | Key Type | Description\n"
        response_text += "-" * 80 + "\n"

        for column in schema_info['columns']:
            column_name = column.get('COLUMN_NAME', '')
            data_type = column.get('DATA_TYPE', '')
            nullable = 'YES' if column.get('IS_NULLABLE') == 'YES' else 'NO'
            default = column.get('COLUMN_DEFAULT', '') or ''
            key_type = 'PK' if column.get('IS_PRIMARY_KEY') else ''
            description = column.get('COLUMN_DESCRIPTION', '') or ''
            response_text += f"{column_name} | {data_type} | {nullable} | {default} | {key_type} | {description}\n"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to get MySQL table schema: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_mysql_list_tables(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MySQL database tables listing."""
    database_name = arguments.get("database_name")

    try:
        tables = mysql_manager.get_database_tables(database_name)
        if not tables:
            response_text = f"No tables found in MySQL database."
        else:
            response_text = f"MySQL Tables ({len(tables)} found):\n\n"
            for i, table in enumerate(tables, 1):
                response_text += f"{i}. {table}\n"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to list MySQL tables: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


# Redis handler functions
async def handle_redis_get(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Redis GET operation."""
    key = arguments.get("key", "")

    try:
        value = redis_manager.get(key)
        if value is None:
            response_text = f"Redis key '{key}' not found."
        else:
            response_text = f"Redis key '{key}' value: {value}"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Redis GET failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_redis_set(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Redis SET operation."""
    key = arguments.get("key", "")
    value = arguments.get("value", "")
    ex = arguments.get("ex")

    try:
        success = redis_manager.set(key, value, ex=ex)
        if success:
            if ex:
                response_text = f"Redis key '{key}' set successfully with expiration {ex} seconds."
            else:
                response_text = f"Redis key '{key}' set successfully."
        else:
            response_text = f"Failed to set Redis key '{key}'."

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Redis SET failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_redis_delete(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Redis DELETE operation."""
    keys = arguments.get("keys", [])

    try:
        deleted_count = redis_manager.delete(*keys)
        response_text = f"Redis deleted {deleted_count} keys out of {len(keys)} requested."
        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Redis DELETE failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_redis_keys(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Redis KEYS operation."""
    pattern = arguments.get("pattern", "*")

    try:
        keys = redis_manager.keys(pattern)
        if not keys:
            response_text = f"No Redis keys found matching pattern '{pattern}'."
        else:
            response_text = f"Redis keys matching '{pattern}' ({len(keys)} found):\n\n"
            for i, key in enumerate(keys[:100], 1):  # Limit to first 100 keys
                response_text += f"{i}. {key}\n"
            if len(keys) > 100:
                response_text += f"\n... and {len(keys) - 100} more keys"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Redis KEYS failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_redis_info(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Redis INFO operation."""
    section = arguments.get("section")

    try:
        info = redis_manager.info(section)
        response_text = f"Redis Server Information"
        if section:
            response_text += f" ({section} section)"
        response_text += ":\n\n"

        # Format the info dictionary
        for key, value in info.items():
            response_text += f"{key}: {value}\n"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Redis INFO failed: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


# Database management functions
async def handle_mysql_reconnect(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MySQL reconnection attempt."""
    try:
        logger.info("Attempting to reconnect to MySQL...")
        success = mysql_manager.reconnect()

        if success:
            return [TextContent(type="text", text="✅ MySQL重连成功！MySQL工具现在可用。")]
        else:
            error_msg = mysql_manager.get_connection_error() or "未知错误"
            return [TextContent(type="text", text=f"❌ MySQL重连失败: {error_msg}")]

    except Exception as e:
        error_msg = f"MySQL重连过程中发生错误: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_redis_reconnect(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Redis reconnection attempt."""
    try:
        logger.info("Attempting to reconnect to Redis...")
        success = redis_manager.reconnect()

        if success:
            return [TextContent(type="text", text="✅ Redis重连成功！Redis工具现在可用。")]
        else:
            error_msg = redis_manager.get_connection_error() or "未知错误"
            return [TextContent(type="text", text=f"❌ Redis重连失败: {error_msg}")]

    except Exception as e:
        error_msg = f"Redis重连过程中发生错误: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_database_reconnect(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle database reconnection attempt."""
    try:
        logger.info("Attempting to reconnect to database...")
        success = db_manager.reconnect()

        if success:
            return [TextContent(type="text", text="✅ 数据库重连成功！数据库工具现在可用。")]
        else:
            error_msg = db_manager.get_connection_error() or "未知错误"
            return [TextContent(type="text", text=f"❌ 数据库重连失败: {error_msg}")]

    except Exception as e:
        error_msg = f"数据库重连过程中发生错误: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_database_status(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle all database connections status check."""
    try:
        status_text = "🗄️ 数据库连接状态报告:\n\n"

        # SQL Server status
        sqlserver_available = db_manager.is_available()
        if sqlserver_available:
            connection_ok = db_manager.test_connection()
            if connection_ok:
                status_text += "✅ SQL Server: 连接正常，工具可用\n"
            else:
                status_text += "⚠️ SQL Server: 标记为可用，但连接测试失败\n"
        else:
            error_msg = db_manager.get_connection_error() or "未知错误"
            status_text += f"❌ SQL Server: 不可用 - {error_msg}\n"

        # MySQL status
        mysql_available = mysql_manager.is_available()
        if mysql_available:
            connection_ok = mysql_manager.test_connection()
            if connection_ok:
                status_text += "✅ MySQL: 连接正常，工具可用\n"
            else:
                status_text += "⚠️ MySQL: 标记为可用，但连接测试失败\n"
        else:
            error_msg = mysql_manager.get_connection_error() or "未知错误"
            status_text += f"❌ MySQL: 不可用 - {error_msg}\n"

        # Redis status
        redis_available = redis_manager.is_available()
        if redis_available:
            connection_ok = redis_manager.test_connection()
            if connection_ok:
                status_text += "✅ Redis: 连接正常，工具可用\n"
            else:
                status_text += "⚠️ Redis: 标记为可用，但连接测试失败\n"
        else:
            error_msg = redis_manager.get_connection_error() or "未知错误"
            status_text += f"❌ Redis: 不可用 - {error_msg}\n"

        # Summary
        available_count = sum([sqlserver_available, mysql_available, redis_available])
        status_text += f"\n📊 总结: {available_count}/3 个数据库服务可用"

        if available_count < 3:
            status_text += "\n💡 提示: 使用相应的重连工具尝试重新连接不可用的服务"

        return [TextContent(type="text", text=status_text)]

    except Exception as e:
        error_msg = f"检查数据库状态时发生错误: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_database_reconnect(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle database reconnection attempt."""
    try:
        logger.info("Attempting to reconnect to database...")
        success = db_manager.reconnect()

        if success:
            return [TextContent(type="text", text="✅ 数据库重连成功！数据库工具现在可用。")]
        else:
            error_msg = db_manager.get_connection_error() or "未知错误"
            return [TextContent(type="text", text=f"❌ 数据库重连失败: {error_msg}")]

    except Exception as e:
        error_msg = f"数据库重连过程中发生错误: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_read_file(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle file reading."""
    file_path = arguments.get("file_path", "")
    encoding = arguments.get("encoding", "utf-8")

    try:
        content = fs_manager.read_file(file_path, encoding)

        # Limit content display for very large files
        if len(content) > 10000:
            preview_content = content[:10000] + f"\n\n... (file truncated, showing first 10000 characters of {len(content)} total)"
            response_text = f"File content from '{file_path}':\n\n{preview_content}"
        else:
            response_text = f"File content from '{file_path}':\n\n{content}"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to read file: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_write_file(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle file writing."""
    file_path = arguments.get("file_path", "")
    content = arguments.get("content", "")
    encoding = arguments.get("encoding", "utf-8")
    create_dirs = arguments.get("create_dirs", True)
    confirm = arguments.get("confirm", True)  # 默认允许覆盖

    try:
        # Check if confirmation is required for overwriting existing files
        from pathlib import Path
        path = Path(file_path)

        # 只有当用户明确设置 confirm=false 时才要求确认
        if path.exists() and confirm is False:
            return [TextContent(
                type="text",
                text=f"File '{file_path}' already exists. Please add 'confirm': true to overwrite."
            )]

        fs_manager.write_file(file_path, content, encoding, create_dirs)

        response_text = f"File written successfully: '{file_path}' ({len(content)} characters)"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to write file: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_list_directory(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle directory listing."""
    dir_path = arguments.get("dir_path", "")
    recursive = arguments.get("recursive", False)

    try:
        items = fs_manager.list_directory(dir_path, recursive)

        if not items:
            response_text = f"Directory '{dir_path}' is empty or no accessible items found."
        else:
            response_text = f"Directory listing for '{dir_path}' ({len(items)} items):\n\n"
            response_text += "Type | Name | Size | Modified\n"
            response_text += "-" * 50 + "\n"

            for item in items:
                item_type = "DIR" if item.get("is_directory") else "FILE"
                name = item.get("name", "")
                size = item.get("size", 0) if not item.get("is_directory") else ""
                modified = item.get("modified", "")

                response_text += f"{item_type} | {name} | {size} | {modified}\n"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to list directory: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_delete_file(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle file deletion."""
    file_path = arguments.get("file_path", "")
    confirm = arguments.get("confirm", True)  # 默认允许删除

    try:
        from pathlib import Path
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return [TextContent(type="text", text=f"File does not exist: '{file_path}'")]

        # 只有当用户明确设置 confirm=false 时才要求确认
        if confirm is False:
            return [TextContent(
                type="text",
                text=f"File deletion requires confirmation. Please add 'confirm': true to delete: '{file_path}'"
            )]

        fs_manager.delete_file(file_path)

        response_text = f"File deleted successfully: '{file_path}'"
        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to delete file: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_create_directory(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle directory creation."""
    dir_path = arguments.get("dir_path", "")
    parents = arguments.get("parents", True)

    try:
        fs_manager.create_directory(dir_path, parents)

        response_text = f"Directory created successfully: '{dir_path}'"
        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        error_msg = f"Failed to create directory: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting MCP Database Filesystem server...")

    # Test all database connections on startup (non-blocking)
    try:
        # Test SQL Server
        if db_manager.test_connection():
            logger.info("SQL Server connection test successful")
        else:
            logger.warning("SQL Server connection test failed - SQL Server tools will be unavailable")

        # Test MySQL
        if mysql_manager.test_connection():
            logger.info("MySQL connection test successful")
        else:
            logger.warning("MySQL connection test failed - MySQL tools will be unavailable")

        # Test Redis
        if redis_manager.test_connection():
            logger.info("Redis connection test successful")
        else:
            logger.warning("Redis connection test failed - Redis tools will be unavailable")

    except Exception as e:
        logger.warning(f"Database connection test error: {e} - some database tools may be unavailable")

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-db-filesystem",
                server_version=__version__,
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(list_changed=True),
                    experimental={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
