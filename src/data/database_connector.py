"""
Database connector for loading campaign data from various database sources.
Supports PostgreSQL, MySQL, SQLite, SQL Server, and more.
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from loguru import logger
import sqlalchemy
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


class DatabaseConnector:
    """Connect to various databases and load campaign data."""
    
    SUPPORTED_DATABASES = {
        'postgresql': 'PostgreSQL',
        'mysql': 'MySQL',
        'sqlite': 'SQLite',
        'mssql': 'SQL Server',
        'oracle': 'Oracle'
    }
    
    def __init__(self):
        """Initialize database connector."""
        self.engine = None
        self.connection_string = None
    
    def build_connection_string(
        self,
        db_type: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: str = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Build database connection string.
        
        Args:
            db_type: Database type (postgresql, mysql, sqlite, mssql, oracle)
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password
            file_path: File path for SQLite
            **kwargs: Additional connection parameters
            
        Returns:
            Connection string
        """
        db_type = db_type.lower()
        
        if db_type not in self.SUPPORTED_DATABASES:
            raise ValueError(f"Unsupported database type: {db_type}. Supported: {list(self.SUPPORTED_DATABASES.keys())}")
        
        # SQLite
        if db_type == 'sqlite':
            if not file_path:
                raise ValueError("file_path is required for SQLite")
            return f"sqlite:///{file_path}"
        
        # Other databases require credentials
        if not all([host, database, username, password]):
            raise ValueError(f"{db_type} requires host, database, username, and password")
        
        # Encode password for special characters
        encoded_password = quote_plus(password)
        
        # PostgreSQL
        if db_type == 'postgresql':
            port = port or 5432
            return f"postgresql://{username}:{encoded_password}@{host}:{port}/{database}"
        
        # MySQL
        elif db_type == 'mysql':
            port = port or 3306
            driver = kwargs.get('driver', 'pymysql')
            return f"mysql+{driver}://{username}:{encoded_password}@{host}:{port}/{database}"
        
        # SQL Server
        elif db_type == 'mssql':
            port = port or 1433
            driver = kwargs.get('driver', 'ODBC Driver 17 for SQL Server')
            return f"mssql+pyodbc://{username}:{encoded_password}@{host}:{port}/{database}?driver={quote_plus(driver)}"
        
        # Oracle
        elif db_type == 'oracle':
            port = port or 1521
            return f"oracle+cx_oracle://{username}:{encoded_password}@{host}:{port}/{database}"
        
        return None
    
    def connect(
        self,
        connection_string: Optional[str] = None,
        db_type: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Connect to database.
        
        Args:
            connection_string: Pre-built connection string
            db_type: Database type (if building connection string)
            **kwargs: Connection parameters for build_connection_string
            
        Returns:
            True if connection successful
        """
        try:
            if connection_string:
                self.connection_string = connection_string
            elif db_type:
                self.connection_string = self.build_connection_string(db_type, **kwargs)
            else:
                raise ValueError("Either connection_string or db_type must be provided")
            
            logger.info(f"Connecting to database...")
            self.engine = create_engine(self.connection_string)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.success("✅ Database connection successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.engine = None
            raise
    
    def get_tables(self) -> List[str]:
        """
        Get list of tables in the database.
        
        Returns:
            List of table names
        """
        if not self.engine:
            raise ValueError("Not connected to database. Call connect() first.")
        
        try:
            inspector = sqlalchemy.inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"Found {len(tables)} tables in database")
            return tables
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            raise
    
    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        """
        Get schema information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            DataFrame with column information
        """
        if not self.engine:
            raise ValueError("Not connected to database. Call connect() first.")
        
        try:
            inspector = sqlalchemy.inspect(self.engine)
            columns = inspector.get_columns(table_name)
            
            schema_df = pd.DataFrame([
                {
                    'column_name': col['name'],
                    'data_type': str(col['type']),
                    'nullable': col['nullable']
                }
                for col in columns
            ])
            
            return schema_df
        except Exception as e:
            logger.error(f"Failed to get schema for {table_name}: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.
        
        Args:
            query: SQL query to execute
            params: Query parameters (for parameterized queries)
            
        Returns:
            DataFrame with query results
        """
        if not self.engine:
            raise ValueError("Not connected to database. Call connect() first.")
        
        try:
            logger.info(f"Executing query: {query[:100]}...")
            
            with self.engine.connect() as conn:
                if params:
                    result = pd.read_sql(text(query), conn, params=params)
                else:
                    result = pd.read_sql(text(query), conn)
            
            logger.success(f"✅ Query executed successfully. Rows: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            raise
    
    def load_table(self, table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Load entire table or limited rows.
        
        Args:
            table_name: Name of the table
            limit: Maximum number of rows to load
            
        Returns:
            DataFrame with table data
        """
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection and return info.
        
        Returns:
            Dictionary with connection info
        """
        if not self.engine:
            return {'connected': False, 'error': 'Not connected'}
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            tables = self.get_tables()
            
            return {
                'connected': True,
                'database_type': self.engine.dialect.name,
                'table_count': len(tables),
                'tables': tables[:10]  # First 10 tables
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
            self.engine = None


# Convenience functions
def connect_to_database(
    db_type: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: str = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    file_path: Optional[str] = None,
    **kwargs
) -> DatabaseConnector:
    """
    Quick connect to database.
    
    Returns:
        Connected DatabaseConnector instance
    """
    connector = DatabaseConnector()
    connector.connect(
        db_type=db_type,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
        file_path=file_path,
        **kwargs
    )
    return connector


def load_from_database(
    query: str,
    db_type: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: str = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    file_path: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Quick load data from database with query.
    
    Returns:
        DataFrame with query results
    """
    connector = connect_to_database(
        db_type=db_type,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
        file_path=file_path,
        **kwargs
    )
    
    try:
        df = connector.execute_query(query)
        return df
    finally:
        connector.close()
