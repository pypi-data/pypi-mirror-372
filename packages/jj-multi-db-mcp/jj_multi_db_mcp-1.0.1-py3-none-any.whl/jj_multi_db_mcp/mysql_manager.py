"""MySQL database manager."""

import os
import logging
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

try:
    import pymysql
    from sqlalchemy import create_engine, text
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

logger = logging.getLogger(__name__)


class MySQLManager:
    """MySQL database manager."""
    
    def __init__(self):
        """Initialize MySQL manager."""
        if not MYSQL_AVAILABLE:
            raise ImportError("MySQL dependencies not installed. Install with: pip install jj-multi-db-mcp[mysql]")
        
        self._engine = None
        self._is_available = False
        self._connection_error = None
        
        # Get configuration from environment variables
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", "3306"))
        self.database = os.getenv("MYSQL_DATABASE", "mysql")
        self.username = os.getenv("MYSQL_USERNAME", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "")
        self.charset = os.getenv("MYSQL_CHARSET", "utf8mb4")
        
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection."""
        try:
            # Build connection string
            connection_string = (
                f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/"
                f"{self.database}?charset={self.charset}"
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
            logger.info(f"MySQL connected successfully: {self.host}:{self.port}/{self.database}")
            
        except Exception as e:
            self._is_available = False
            self._connection_error = str(e)
            logger.error(f"MySQL connection failed: {e}")
    
    def is_available(self) -> bool:
        """Check if MySQL is available."""
        return self._is_available
    
    def get_connection_error(self) -> Optional[str]:
        """Get connection error message."""
        return self._connection_error
    
    @contextmanager
    def get_connection(self):
        """Get a database connection."""
        if not self._is_available:
            raise Exception(f"MySQL is not available: {self._connection_error}")
        
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
        query = "SHOW TABLES"
        result = self.execute_query(query)
        # MySQL returns table names in a column named 'Tables_in_{database_name}'
        if result['rows']:
            table_column = result['columns'][0]
            return [row[table_column] for row in result['rows']]
        return []
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a table."""
        query = f"DESCRIBE {table_name}"
        result = self.execute_query(query)
        
        schema = []
        for row in result['rows']:
            schema.append({
                'column_name': row['Field'],
                'data_type': row['Type'],
                'is_nullable': row['Null'] == 'YES',
                'column_default': row['Default'],
                'key': row['Key'],
                'extra': row['Extra']
            })
        
        return schema
