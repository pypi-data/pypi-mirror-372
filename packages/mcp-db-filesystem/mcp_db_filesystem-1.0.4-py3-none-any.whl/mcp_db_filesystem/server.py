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

    # Add database tools only if database is available
    if db_manager.is_available():
        tools.extend([
            # Database tools
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

    # Always add database management tools
    tools.extend([
        # Database management tools
        Tool(
            name="database_reconnect",
            description="Attempt to reconnect to the database",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="database_status",
            description="Check database connection status",
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
    ])

    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        # Database tools - check availability first
        if name in ["sql_query", "sql_execute", "get_table_schema", "list_tables"]:
            if not db_manager.is_available():
                error_msg = f"❌ 数据库工具不可用: {db_manager.get_connection_error()}"
                return [TextContent(type="text", text=error_msg)]

        if name == "sql_query":
            return await handle_sql_query(arguments)
        elif name == "sql_execute":
            return await handle_sql_execute(arguments)
        elif name == "get_table_schema":
            return await handle_get_table_schema(arguments)
        elif name == "list_tables":
            return await handle_list_tables(arguments)
        elif name == "database_reconnect":
            return await handle_database_reconnect(arguments)
        elif name == "database_status":
            return await handle_database_status(arguments)
        elif name == "read_file":
            return await handle_read_file(arguments)
        elif name == "write_file":
            return await handle_write_file(arguments)
        elif name == "list_directory":
            return await handle_list_directory(arguments)

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
    """Handle database status check."""
    try:
        is_available = db_manager.is_available()

        if is_available:
            # Test actual connection
            connection_ok = db_manager.test_connection()
            if connection_ok:
                status_text = "✅ 数据库连接正常，所有数据库工具可用。"
            else:
                status_text = "⚠️ 数据库标记为可用，但连接测试失败。尝试重连可能有帮助。"
        else:
            error_msg = db_manager.get_connection_error() or "未知错误"
            status_text = f"❌ 数据库不可用: {error_msg}\n💡 提示：使用 database_reconnect 工具尝试重新连接"

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


async def handle_database_status(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle database status check."""
    try:
        is_available = db_manager.is_available()

        if is_available:
            # Test actual connection
            connection_ok = db_manager.test_connection()
            if connection_ok:
                status_text = "✅ 数据库连接正常，所有数据库工具可用。"
            else:
                status_text = "⚠️ 数据库标记为可用，但连接测试失败。尝试重连可能有帮助。"
        else:
            error_msg = db_manager.get_connection_error() or "未知错误"
            status_text = f"❌ 数据库不可用: {error_msg}\n💡 提示：使用 database_reconnect 工具尝试重新连接"

        return [TextContent(type="text", text=status_text)]

    except Exception as e:
        error_msg = f"检查数据库状态时发生错误: {str(e)}"
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
    confirm = arguments.get("confirm", False)

    try:
        # Check if confirmation is required for overwriting existing files
        from pathlib import Path
        path = Path(file_path)

        if path.exists() and not confirm:
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


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting MCP Database Filesystem server...")

    # Test database connection on startup (non-blocking)
    try:
        if db_manager.test_connection():
            logger.info("Database connection test successful")
        else:
            logger.warning("Database connection test failed - database tools will be unavailable")
    except Exception as e:
        logger.warning(f"Database connection test error: {e} - database tools will be unavailable")

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
