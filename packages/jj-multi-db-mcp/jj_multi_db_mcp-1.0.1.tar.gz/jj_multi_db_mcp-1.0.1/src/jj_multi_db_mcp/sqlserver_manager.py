"""SQL Server database manager."""

import os
import logging
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

try:
    import pyodbc
    from sqlalchemy import create_engine, text
    SQLSERVER_AVAILABLE = True
except ImportError:
    SQLSERVER_AVAILABLE = False

logger = logging.getLogger(__name__)


class SQLServerManager:
    """SQL Server database manager."""
    
    def __init__(self):
        """Initialize SQL Server manager."""
        if not SQLSERVER_AVAILABLE:
            raise ImportError("SQL Server dependencies not installed. Install with: pip install jj-multi-db-mcp[sqlserver]")
        
        self._engine = None
        self._is_available = False
        self._connection_error = None
        
        # Get configuration from environment variables
        self.host = os.getenv("SQLSERVER_HOST", "localhost")
        self.port = os.getenv("SQLSERVER_PORT", "1433")
        self.database = os.getenv("SQLSERVER_DATABASE", "master")
        self.username = os.getenv("SQLSERVER_USERNAME", "sa")
        self.password = os.getenv("SQLSERVER_PASSWORD", "")
        self.driver = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")
        
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection."""
        try:
            # Build connection string
            connection_string = (
                f"mssql+pyodbc://{self.username}:{self.password}@{self.host}:{self.port}/"
                f"{self.database}?driver={self.driver.replace(' ', '+')}"
            )
            
            self._engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            # Test connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self._is_available = True
            self._connection_error = None
            logger.info(f"SQL Server connected successfully: {self.host}:{self.port}/{self.database}")
            
        except Exception as e:
            self._is_available = False
            self._connection_error = str(e)
            logger.error(f"SQL Server connection failed: {e}")
    
    def is_available(self) -> bool:
        """Check if SQL Server is available."""
        return self._is_available
    
    def get_connection_error(self) -> Optional[str]:
        """Get connection error message."""
        return self._connection_error
    
    @contextmanager
    def get_connection(self):
        """Get a database connection."""
        if not self._is_available:
            raise Exception(f"SQL Server is not available: {self._connection_error}")
        
        connection = None
        try:
            connection = self._engine.connect()
            yield connection
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a SELECT query."""
        with self.get_connection() as conn:
            result = conn.execute(text(query), parameters or {})
            
            columns = list(result.keys())
            rows = []
            for row in result:
                row_dict = {}
                for i, col_name in enumerate(columns):
                    row_dict[col_name] = row[i]
                rows.append(row_dict)
            
            return {
                'columns': columns,
                'rows': rows,
                'row_count': len(rows)
            }
    
    def execute_non_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query."""
        with self.get_connection() as conn:
            result = conn.execute(text(query), parameters or {})
            conn.commit()
            return result.rowcount
    
    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        result = self.execute_query(query)
        return [row['TABLE_NAME'] for row in result['rows']]
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a table."""
        query = """
        SELECT 
            COLUMN_NAME as column_name,
            DATA_TYPE as data_type,
            IS_NULLABLE as is_nullable,
            COLUMN_DEFAULT as column_default,
            CHARACTER_MAXIMUM_LENGTH as max_length
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = :table_name
        ORDER BY ORDINAL_POSITION
        """
        result = self.execute_query(query, {"table_name": table_name})
        
        schema = []
        for row in result['rows']:
            schema.append({
                'column_name': row['column_name'],
                'data_type': row['data_type'],
                'is_nullable': row['is_nullable'] == 'YES',
                'column_default': row['column_default'],
                'max_length': row['max_length']
            })
        
        return schema
