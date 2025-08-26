"""
JJ Multi-Database MCP Server
A simple MCP server supporting SQL Server, MySQL, Oracle, Redis and filesystem operations.
Based on mcp-sqlserver-filesystem architecture.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    ServerCapabilities,
    ToolsCapability,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("jj-multi-db-mcp")

# Database managers (will be initialized based on environment variables)
sqlserver_manager = None
mysql_manager = None
oracle_manager = None
redis_manager = None

def initialize_managers():
    """Initialize database managers based on environment variables."""
    global sqlserver_manager, mysql_manager, oracle_manager, redis_manager, fs_manager

    # Initialize filesystem manager (always available)
    from .filesystem import FilesystemManager
    fs_manager = FilesystemManager()
    
    # SQL Server
    if os.getenv("SQLSERVER_ENABLED", "false").lower() == "true":
        try:
            from .sqlserver_manager import SQLServerManager
            sqlserver_manager = SQLServerManager()
            logger.info(f"SQL Server manager initialized: {'available' if sqlserver_manager.is_available() else 'unavailable'}")
        except ImportError:
            logger.warning("SQL Server dependencies not installed. Install with: pip install jj-multi-db-mcp[sqlserver]")
        except Exception as e:
            logger.error(f"Failed to initialize SQL Server manager: {e}")
    
    # MySQL
    if os.getenv("MYSQL_ENABLED", "false").lower() == "true":
        try:
            from .mysql_manager import MySQLManager
            mysql_manager = MySQLManager()
            logger.info(f"MySQL manager initialized: {'available' if mysql_manager.is_available() else 'unavailable'}")
        except ImportError:
            logger.warning("MySQL dependencies not installed. Install with: pip install jj-multi-db-mcp[mysql]")
        except Exception as e:
            logger.error(f"Failed to initialize MySQL manager: {e}")
    
    # Oracle
    if os.getenv("ORACLE_ENABLED", "false").lower() == "true":
        try:
            from .oracle_manager import OracleManager
            oracle_manager = OracleManager()
            logger.info(f"Oracle manager initialized: {'available' if oracle_manager.is_available() else 'unavailable'}")
        except ImportError:
            logger.warning("Oracle dependencies not installed. Install with: pip install jj-multi-db-mcp[oracle]")
        except Exception as e:
            logger.error(f"Failed to initialize Oracle manager: {e}")
    
    # Redis
    if os.getenv("REDIS_ENABLED", "false").lower() == "true":
        try:
            from .redis_manager import RedisManager
            redis_manager = RedisManager()
            logger.info(f"Redis manager initialized: {'available' if redis_manager.is_available() else 'unavailable'}")
        except ImportError:
            logger.warning("Redis dependencies not installed. Install with: pip install jj-multi-db-mcp[redis]")
        except Exception as e:
            logger.error(f"Failed to initialize Redis manager: {e}")

# Filesystem manager will be initialized in initialize_managers()
fs_manager = None

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources."""
    resources = [
        Resource(
            uri="status://databases",
            name="Database Status",
            description="Current database connection status",
            mimeType="application/json",
        ),
    ]
    return resources

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    if uri == "status://databases":
        status = {
            "sqlserver": {
                "enabled": sqlserver_manager is not None,
                "available": sqlserver_manager.is_available() if sqlserver_manager else False,
                "error": sqlserver_manager.get_connection_error() if sqlserver_manager else None
            },
            "mysql": {
                "enabled": mysql_manager is not None,
                "available": mysql_manager.is_available() if mysql_manager else False,
                "error": mysql_manager.get_connection_error() if mysql_manager else None
            },
            "oracle": {
                "enabled": oracle_manager is not None,
                "available": oracle_manager.is_available() if oracle_manager else False,
                "error": oracle_manager.get_connection_error() if oracle_manager else None
            },
            "redis": {
                "enabled": redis_manager is not None,
                "available": redis_manager.is_available() if redis_manager else False,
                "error": redis_manager.get_connection_error() if redis_manager else None
            }
        }
        import json
        return json.dumps(status, indent=2)
    
    raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    tools = []
    
    # Filesystem tools
    tools.extend([
        Tool(
            name="read_file",
            description="Read content from a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to read"},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to write"},
                    "content": {"type": "string", "description": "Content to write to the file"},
                },
                "required": ["path", "content"],
            },
        ),
        Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the directory to list"},
                },
                "required": ["path"],
            },
        ),
    ])
    
    # SQL Server tools
    if sqlserver_manager:
        tools.extend([
            Tool(
                name="sqlserver_query",
                description="Execute a SELECT query on SQL Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL SELECT query to execute"},
                        "parameters": {"type": "object", "description": "Query parameters (optional)"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="sqlserver_execute",
                description="Execute an INSERT, UPDATE, or DELETE query on SQL Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query to execute"},
                        "parameters": {"type": "object", "description": "Query parameters (optional)"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="sqlserver_list_tables",
                description="List all tables in SQL Server database",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="sqlserver_table_schema",
                description="Get schema information for a SQL Server table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                    },
                    "required": ["table_name"],
                },
            ),
        ])
    
    # MySQL tools
    if mysql_manager:
        tools.extend([
            Tool(
                name="mysql_query",
                description="Execute a SELECT query on MySQL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL SELECT query to execute"},
                        "parameters": {"type": "object", "description": "Query parameters (optional)"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="mysql_execute",
                description="Execute an INSERT, UPDATE, or DELETE query on MySQL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query to execute"},
                        "parameters": {"type": "object", "description": "Query parameters (optional)"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="mysql_list_tables",
                description="List all tables in MySQL database",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="mysql_table_schema",
                description="Get schema information for a MySQL table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                    },
                    "required": ["table_name"],
                },
            ),
        ])
    
    # Oracle tools
    if oracle_manager:
        tools.extend([
            Tool(
                name="oracle_query",
                description="Execute a SELECT query on Oracle",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL SELECT query to execute"},
                        "parameters": {"type": "object", "description": "Query parameters (optional)"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="oracle_execute",
                description="Execute an INSERT, UPDATE, or DELETE query on Oracle",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query to execute"},
                        "parameters": {"type": "object", "description": "Query parameters (optional)"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="oracle_list_tables",
                description="List all tables in Oracle database",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="oracle_table_schema",
                description="Get schema information for an Oracle table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                    },
                    "required": ["table_name"],
                },
            ),
        ])
    
    # Redis tools
    if redis_manager:
        tools.extend([
            Tool(
                name="redis_get",
                description="Get value from Redis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Redis key to get"},
                    },
                    "required": ["key"],
                },
            ),
            Tool(
                name="redis_set",
                description="Set value in Redis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Redis key to set"},
                        "value": {"type": "string", "description": "Value to set"},
                        "expire": {"type": "integer", "description": "Expiration time in seconds (optional)"},
                    },
                    "required": ["key", "value"],
                },
            ),
            Tool(
                name="redis_delete",
                description="Delete key from Redis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Redis key to delete"},
                    },
                    "required": ["key"],
                },
            ),
            Tool(
                name="redis_keys",
                description="Get keys matching pattern from Redis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Pattern to match (default: '*')"},
                    },
                },
            ),
        ])
    
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    try:
        # Filesystem tools
        if name == "read_file":
            content = fs_manager.read_file(arguments["path"])
            return [TextContent(type="text", text=content)]

        elif name == "write_file":
            fs_manager.write_file(arguments["path"], arguments["content"])
            return [TextContent(type="text", text=f"✅ File written successfully: {arguments['path']}")]

        elif name == "list_directory":
            items = fs_manager.list_directory(arguments["path"])
            result = "\n".join([f"{'📁' if item['type'] == 'directory' else '📄'} {item['name']}" for item in items])
            return [TextContent(type="text", text=result)]

        # SQL Server tools
        elif name == "sqlserver_query":
            if not sqlserver_manager or not sqlserver_manager.is_available():
                return [TextContent(type="text", text="❌ SQL Server is not available")]

            result = sqlserver_manager.execute_query(arguments["query"], arguments.get("parameters"))
            formatted_result = format_query_result(result)
            return [TextContent(type="text", text=formatted_result)]

        elif name == "sqlserver_execute":
            if not sqlserver_manager or not sqlserver_manager.is_available():
                return [TextContent(type="text", text="❌ SQL Server is not available")]

            affected_rows = sqlserver_manager.execute_non_query(arguments["query"], arguments.get("parameters"))
            return [TextContent(type="text", text=f"✅ Query executed successfully. Affected rows: {affected_rows}")]

        elif name == "sqlserver_list_tables":
            if not sqlserver_manager or not sqlserver_manager.is_available():
                return [TextContent(type="text", text="❌ SQL Server is not available")]

            tables = sqlserver_manager.list_tables()
            result = "\n".join([f"📋 {table}" for table in tables])
            return [TextContent(type="text", text=result)]

        elif name == "sqlserver_table_schema":
            if not sqlserver_manager or not sqlserver_manager.is_available():
                return [TextContent(type="text", text="❌ SQL Server is not available")]

            schema = sqlserver_manager.get_table_schema(arguments["table_name"])
            formatted_schema = format_table_schema(schema)
            return [TextContent(type="text", text=formatted_schema)]

        # MySQL tools
        elif name == "mysql_query":
            if not mysql_manager or not mysql_manager.is_available():
                return [TextContent(type="text", text="❌ MySQL is not available")]

            result = mysql_manager.execute_query(arguments["query"], arguments.get("parameters"))
            formatted_result = format_query_result(result)
            return [TextContent(type="text", text=formatted_result)]

        elif name == "mysql_execute":
            if not mysql_manager or not mysql_manager.is_available():
                return [TextContent(type="text", text="❌ MySQL is not available")]

            affected_rows = mysql_manager.execute_non_query(arguments["query"], arguments.get("parameters"))
            return [TextContent(type="text", text=f"✅ Query executed successfully. Affected rows: {affected_rows}")]

        elif name == "mysql_list_tables":
            if not mysql_manager or not mysql_manager.is_available():
                return [TextContent(type="text", text="❌ MySQL is not available")]

            tables = mysql_manager.list_tables()
            result = "\n".join([f"📋 {table}" for table in tables])
            return [TextContent(type="text", text=result)]

        elif name == "mysql_table_schema":
            if not mysql_manager or not mysql_manager.is_available():
                return [TextContent(type="text", text="❌ MySQL is not available")]

            schema = mysql_manager.get_table_schema(arguments["table_name"])
            formatted_schema = format_table_schema(schema)
            return [TextContent(type="text", text=formatted_schema)]

        # Oracle tools
        elif name == "oracle_query":
            if not oracle_manager or not oracle_manager.is_available():
                return [TextContent(type="text", text="❌ Oracle is not available")]

            result = oracle_manager.execute_query(arguments["query"], arguments.get("parameters"))
            formatted_result = format_query_result(result)
            return [TextContent(type="text", text=formatted_result)]

        elif name == "oracle_execute":
            if not oracle_manager or not oracle_manager.is_available():
                return [TextContent(type="text", text="❌ Oracle is not available")]

            affected_rows = oracle_manager.execute_non_query(arguments["query"], arguments.get("parameters"))
            return [TextContent(type="text", text=f"✅ Query executed successfully. Affected rows: {affected_rows}")]

        elif name == "oracle_list_tables":
            if not oracle_manager or not oracle_manager.is_available():
                return [TextContent(type="text", text="❌ Oracle is not available")]

            tables = oracle_manager.list_tables()
            result = "\n".join([f"📋 {table}" for table in tables])
            return [TextContent(type="text", text=result)]

        elif name == "oracle_table_schema":
            if not oracle_manager or not oracle_manager.is_available():
                return [TextContent(type="text", text="❌ Oracle is not available")]

            schema = oracle_manager.get_table_schema(arguments["table_name"])
            formatted_schema = format_table_schema(schema)
            return [TextContent(type="text", text=formatted_schema)]

        # Redis tools
        elif name == "redis_get":
            if not redis_manager or not redis_manager.is_available():
                return [TextContent(type="text", text="❌ Redis is not available")]

            value = redis_manager.get(arguments["key"])
            return [TextContent(type="text", text=f"Value: {value}" if value is not None else "Key not found")]

        elif name == "redis_set":
            if not redis_manager or not redis_manager.is_available():
                return [TextContent(type="text", text="❌ Redis is not available")]

            redis_manager.set(arguments["key"], arguments["value"], arguments.get("expire"))
            return [TextContent(type="text", text=f"✅ Key '{arguments['key']}' set successfully")]

        elif name == "redis_delete":
            if not redis_manager or not redis_manager.is_available():
                return [TextContent(type="text", text="❌ Redis is not available")]

            deleted = redis_manager.delete(arguments["key"])
            return [TextContent(type="text", text=f"✅ Deleted {deleted} key(s)")]

        elif name == "redis_keys":
            if not redis_manager or not redis_manager.is_available():
                return [TextContent(type="text", text="❌ Redis is not available")]

            pattern = arguments.get("pattern", "*")
            keys = redis_manager.keys(pattern)
            result = "\n".join([f"🔑 {key}" for key in keys])
            return [TextContent(type="text", text=result if keys else "No keys found")]

        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool call error: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]

def format_query_result(result: Dict[str, Any]) -> str:
    """Format query result for display."""
    if not result.get("rows"):
        return "No results found."

    columns = result.get("columns", [])
    rows = result.get("rows", [])

    # Create table header
    header = " | ".join(columns)
    separator = "-" * len(header)

    # Create table rows
    table_rows = []
    for row in rows[:100]:  # Limit to 100 rows for display
        row_values = [str(row.get(col, "")) for col in columns]
        table_rows.append(" | ".join(row_values))

    result_text = f"{header}\n{separator}\n" + "\n".join(table_rows)

    if len(rows) > 100:
        result_text += f"\n... ({len(rows) - 100} more rows)"

    result_text += f"\n\nTotal rows: {result.get('row_count', len(rows))}"
    return result_text

def format_table_schema(schema: List[Dict[str, Any]]) -> str:
    """Format table schema for display."""
    if not schema:
        return "No schema information available."

    result = "Column Name | Data Type | Nullable | Default\n"
    result += "-" * 50 + "\n"

    for column in schema:
        name = column.get("column_name", "")
        data_type = column.get("data_type", "")
        nullable = "YES" if column.get("is_nullable", True) else "NO"
        default = column.get("column_default", "")

        result += f"{name} | {data_type} | {nullable} | {default}\n"

    return result

async def main():
    """Main entry point."""
    try:
        # Initialize database managers
        initialize_managers()

        # Show filesystem access mode
        if fs_manager.is_full_access_mode():
            print("⚠️  Filesystem in FULL ACCESS mode - can access all disk files!")
            print("Consider restricting access by setting FS_ALLOWED_PATHS for production use")

        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jj-multi-db-mcp",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools=ToolsCapability()
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())
