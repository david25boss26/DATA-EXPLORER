"""
Database service for managing data storage and queries
Uses DuckDB for fast analytical queries
"""

import os
import pandas as pd
from typing import Dict, Any, List, Optional
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


class DatabaseManager:
    """Manages database operations using DuckDB"""
    
    def __init__(self, db_path: str = "data_explorer.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.engine = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database connection"""
        try:
            # Create DuckDB engine
            self.engine = create_engine(f"duckdb:///{self.db_path}")
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Create a table from a pandas DataFrame"""
        try:
            # Clean table name (remove special characters)
            clean_table_name = self._clean_table_name(table_name)
            
            # Write DataFrame to database
            df.to_sql(
                clean_table_name, 
                self.engine, 
                if_exists='replace', 
                index=False,
                method='multi'
            )
            
            # Get table info
            table_info = self.get_table_info(clean_table_name)
            
            return {
                "success": True,
                "table_name": clean_table_name,
                "rows": len(df),
                "columns": len(df.columns),
                "info": table_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                
                # Check if it's a SELECT query
                if result.returns_rows:
                    # Fetch all rows
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    # Convert to list of dictionaries
                    data = [dict(zip(columns, row)) for row in rows]
                    
                    return {
                        "success": True,
                        "data": data,
                        "columns": list(columns),
                        "row_count": len(data),
                        "query": query
                    }
                else:
                    # For non-SELECT queries (INSERT, UPDATE, DELETE, etc.)
                    return {
                        "success": True,
                        "message": "Query executed successfully",
                        "affected_rows": result.rowcount,
                        "query": query
                    }
                    
        except SQLAlchemyError as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "query": query
            }
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table"""
        try:
            with self.engine.connect() as conn:
                # Get table schema
                schema_query = f"DESCRIBE {table_name}"
                schema_result = conn.execute(text(schema_query))
                schema_data = [dict(zip(schema_result.keys(), row)) for row in schema_result.fetchall()]
                
                # Get row count
                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                count_result = conn.execute(text(count_query))
                row_count = count_result.fetchone()[0]
                
                # Get sample data
                sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                sample_result = conn.execute(text(sample_query))
                sample_data = [dict(zip(sample_result.keys(), row)) for row in sample_result.fetchall()]
                
                return {
                    "schema": schema_data,
                    "row_count": row_count,
                    "sample_data": sample_data,
                    "columns": [col['column_name'] for col in schema_data]
                }
                
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def list_tables(self) -> List[Dict[str, Any]]:
        """List all tables in the database"""
        try:
            with self.engine.connect() as conn:
                # Get list of tables
                tables_query = "SHOW TABLES"
                result = conn.execute(text(tables_query))
                tables = [dict(zip(result.keys(), row)) for row in result.fetchall()]
                
                # Get info for each table
                table_info = []
                for table in tables:
                    table_name = table['name']
                    info = self.get_table_info(table_name)
                    table_info.append({
                        "name": table_name,
                        "info": info
                    })
                
                return table_info
                
        except Exception as e:
            return [{"error": str(e)}]
    
    def delete_table(self, table_name: str) -> Dict[str, Any]:
        """Delete a table from the database"""
        try:
            clean_table_name = self._clean_table_name(table_name)
            
            with self.engine.connect() as conn:
                drop_query = f"DROP TABLE IF EXISTS {clean_table_name}"
                conn.execute(text(drop_query))
                conn.commit()
            
            return {
                "success": True,
                "message": f"Table {clean_table_name} deleted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_table_data(self, table_name: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get data from a table with pagination"""
        try:
            clean_table_name = self._clean_table_name(table_name)
            
            with self.engine.connect() as conn:
                # Get total count
                count_query = f"SELECT COUNT(*) as count FROM {clean_table_name}"
                count_result = conn.execute(text(count_query))
                total_count = count_result.fetchone()[0]
                
                # Get paginated data
                data_query = f"SELECT * FROM {clean_table_name} LIMIT {limit} OFFSET {offset}"
                data_result = conn.execute(text(data_query))
                data = [dict(zip(data_result.keys(), row)) for row in data_result.fetchall()]
                
                return {
                    "success": True,
                    "data": data,
                    "columns": list(data_result.keys()) if data else [],
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total_count
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _clean_table_name(self, table_name: str) -> str:
        """Clean table name to be SQL-safe"""
        # Remove special characters and replace with underscores
        import re
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name)
        # Ensure it starts with a letter or underscore
        if clean_name and not clean_name[0].isalpha() and clean_name[0] != '_':
            clean_name = f"table_{clean_name}"
        return clean_name.lower()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            print("Database connection closed")


# Global database instance
db_manager = DatabaseManager() 