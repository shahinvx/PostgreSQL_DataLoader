"""
PostgreSQL DataLoader - A Python toolkit for PostgreSQL database operations

This module provides a comprehensive class-based interface for PostgreSQL
database operations with pandas DataFrame integration.

Author: PostgreSQL DataLoader Contributors
License: MIT
"""

import os
import psycopg2
from psycopg2 import OperationalError
from typing import Optional, List, Tuple, Any, Dict
from psycopg2.extras import execute_values
import pandas as pd
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


class PostgreSQLDataLoader:
    """
    A comprehensive class for PostgreSQL database operations with pandas integration.

    This class provides methods for:
    - Database connection management
    - Table creation from DataFrames
    - Data insertion with validation
    - Table management (drop, truncate)
    - Database exploration

    Attributes:
        host (str): Database host address
        port (str): Database port number
        database (str): Database name
        user (str): Database username
        password (str): Database password
        connection (psycopg2.connection): Active database connection (if connected)

    Example:
        >>> loader = PostgreSQLDataLoader(
        ...     host="localhost",
        ...     database="mydb",
        ...     user="postgres",
        ...     password="secret"
        ... )
        >>> df = pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']})
        >>> loader.create_table_from_dataframe(df, "users")
        >>> loader.insert_dataframe(df, "users")
    """

    def __init__(self, host: str = None, port: str = None, database: str = None,
                 user: str = None, password: str = None):
        """
        Initialize PostgreSQL DataLoader with connection parameters.

        Parameters can be provided directly or loaded from environment variables.
        Environment variables: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

        Args:
            host (str, optional): Database host. Defaults to localhost or DB_HOST env var.
            port (str, optional): Database port. Defaults to 5432 or DB_PORT env var.
            database (str, optional): Database name. Defaults to DB_NAME env var.
            user (str, optional): Database user. Defaults to postgres or DB_USER env var.
            password (str, optional): Database password. Defaults to DB_PASSWORD env var.
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or os.getenv('DB_PORT', '5432')
        self.database = database or os.getenv('DB_NAME', 'postgres')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.connection = None

    def connect(self) -> bool:
        """
        Establish connection to PostgreSQL database.

        Returns:
            bool: True if connection successful, False otherwise.

        Example:
            >>> loader = PostgreSQLDataLoader()
            >>> if loader.connect():
            ...     print("Connected!")
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return True
        except OperationalError as e:
            print(f"[ERROR] Database connection failed: {e}")
            print("Please check your connection details and ensure PostgreSQL is running.")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error during connection: {e}")
            return False

    def disconnect(self):
        """
        Close the database connection.

        Example:
            >>> loader.disconnect()
        """
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """Context manager entry - establishes connection."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes connection."""
        self.disconnect()

    def get_connection(self):
        """
        Get current connection or create new one.

        Returns:
            psycopg2.connection: Active database connection.

        Raises:
            ConnectionError: If unable to establish connection.
        """
        if not self.connection or self.connection.closed:
            if not self.connect():
                raise ConnectionError("Failed to establish database connection")
        return self.connection

    def _map_dtype_to_postgres(self, dtype) -> str:
        """
        Map pandas data type to PostgreSQL data type.

        Args:
            dtype: Pandas data type

        Returns:
            str: PostgreSQL data type
        """
        dtype_str = str(dtype)
        if 'int' in dtype_str:
            return 'INTEGER'
        elif 'float' in dtype_str:
            return 'DOUBLE PRECISION'
        elif 'bool' in dtype_str:
            return 'BOOLEAN'
        elif 'datetime' in dtype_str:
            return 'TIMESTAMP'
        elif 'date' in dtype_str:
            return 'DATE'
        else:
            return 'TEXT'

    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str,
                                   primary_key: Optional[str] = None,
                                   if_exists: str = 'skip') -> bool:
        """
        Create a PostgreSQL table based on DataFrame schema.

        Args:
            df (pd.DataFrame): DataFrame whose schema defines table structure
            table_name (str): Name of table to create
            primary_key (str, optional): Column to set as primary key
            if_exists (str): Action if table exists: 'skip', 'replace', 'fail'

        Returns:
            bool: True if successful, False otherwise

        Example:
            >>> df = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
            >>> loader.create_table_from_dataframe(df, "users", primary_key="id")
        """
        if df.empty:
            print("[WARNING] DataFrame is empty. Creating table from column names only.")

        if not table_name:
            print("[ERROR] Table name cannot be empty.")
            return False

        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            # Handle if_exists parameter
            if if_exists == 'replace':
                cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            elif if_exists == 'fail':
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = %s
                    );
                """, (table_name,))
                if cur.fetchone()[0]:
                    print(f"[ERROR] Table '{table_name}' already exists (if_exists='fail')")
                    return False

            # Build CREATE TABLE query
            columns_definitions = []
            for col_name, dtype in df.dtypes.items():
                pg_type = self._map_dtype_to_postgres(dtype)
                col_def = f'"{col_name}" {pg_type}'

                if primary_key and col_name == primary_key:
                    col_def += " PRIMARY KEY"

                columns_definitions.append(col_def)

            columns_sql = ", ".join(columns_definitions)
            create_clause = "CREATE TABLE IF NOT EXISTS" if if_exists == 'skip' else "CREATE TABLE"
            CREATE_QUERY = f"{create_clause} {table_name} ({columns_sql});"

            print(f"Creating table '{table_name}'...")
            cur.execute(CREATE_QUERY)
            conn.commit()

            print(f"[OK] Table '{table_name}' created successfully.")
            cur.close()
            return True

        except OperationalError as e:
            print(f"[ERROR] Database operation error: {e}")
            if conn:
                conn.rollback()
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            if conn:
                conn.rollback()
            return False

    def insert_dataframe(self, df: pd.DataFrame, table_name: str,
                        batch_size: int = 1000) -> Optional[int]:
        """
        Insert DataFrame rows into existing table with validation.

        Args:
            df (pd.DataFrame): DataFrame containing data to insert
            table_name (str): Target table name
            batch_size (int): Number of rows per batch insert (default: 1000)

        Returns:
            int or None: Number of rows inserted, or None if failed

        Example:
            >>> df = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
            >>> rows = loader.insert_dataframe(df, "users")
            >>> print(f"Inserted {rows} rows")
        """
        if df.empty:
            print("[WARNING] DataFrame is empty. No rows inserted.")
            return 0

        if not table_name:
            print("[ERROR] Table name cannot be empty.")
            return None

        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            # Get table columns from database
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))

            db_columns = [col[0] for col in cur.fetchall()]

            if not db_columns:
                print(f"[ERROR] Table '{table_name}' not found in database.")
                return None

            # Validate DataFrame columns match table
            df_columns_set = set(df.columns)
            missing_cols = [col for col in db_columns if col not in df_columns_set]

            if missing_cols:
                print(f"[ERROR] Missing columns in DataFrame: {missing_cols}")
                print(f"Required: {db_columns}")
                print(f"Provided: {list(df.columns)}")
                return None

            # Prepare data for insertion
            data_values = df[db_columns].values.tolist()
            quoted_columns = [f'"{col}"' for col in db_columns]
            columns_sql = f"({', '.join(quoted_columns)})"

            INSERT_QUERY = f"INSERT INTO {table_name} {columns_sql} VALUES %s"

            print(f"Inserting {len(data_values)} rows into '{table_name}'...")

            execute_values(cur, INSERT_QUERY, data_values, page_size=batch_size)
            conn.commit()

            inserted_count = cur.rowcount
            print(f"[OK] {inserted_count} row(s) inserted successfully.")

            cur.close()
            return inserted_count

        except OperationalError as e:
            print(f"[ERROR] Database operation error: {e}")
            if conn:
                conn.rollback()
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            if conn:
                conn.rollback()
            return None

    def drop_table(self, table_name: str, cascade: bool = False) -> bool:
        """
        Drop (delete) a table from the database.

        Args:
            table_name (str): Name of table to drop
            cascade (bool): If True, drop dependent objects (default: False)

        Returns:
            bool: True if successful, False otherwise

        Example:
            >>> loader.drop_table("old_table", cascade=True)
        """
        if not table_name:
            print("[ERROR] Table name cannot be empty.")
            return False

        cascade_clause = "CASCADE" if cascade else "RESTRICT"
        DROP_QUERY = f"DROP TABLE IF EXISTS {table_name} {cascade_clause};"

        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            print(f"Dropping table '{table_name}'...")
            cur.execute(DROP_QUERY)
            conn.commit()

            print(f"[OK] Table '{table_name}' dropped successfully.")
            cur.close()
            return True

        except OperationalError as e:
            print(f"[ERROR] Database operation error: {e}")
            if conn:
                conn.rollback()
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            if conn:
                conn.rollback()
            return False

    def truncate_table(self, table_name: str, restart_identity: bool = True) -> bool:
        """
        Remove all rows from table while preserving structure.

        Args:
            table_name (str): Table to truncate
            restart_identity (bool): Reset auto-increment sequences (default: True)

        Returns:
            bool: True if successful, False otherwise

        Example:
            >>> loader.truncate_table("temp_data")
        """
        if not table_name:
            print("[ERROR] Table name cannot be empty.")
            return False

        restart_clause = "RESTART IDENTITY" if restart_identity else ""
        TRUNCATE_QUERY = f"TRUNCATE TABLE {table_name} {restart_clause} CASCADE;"

        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            print(f"Truncating table '{table_name}'...")
            cur.execute(TRUNCATE_QUERY)
            conn.commit()

            print(f"[OK] Table '{table_name}' truncated successfully.")
            cur.close()
            return True

        except OperationalError as e:
            print(f"[ERROR] Database operation error: {e}")
            if conn:
                conn.rollback()
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            if conn:
                conn.rollback()
            return False

    def get_all_tables(self) -> Optional[List[str]]:
        """
        Get list of all user-defined tables in database.

        Returns:
            List[str] or None: List of table names, or None if error

        Example:
            >>> tables = loader.get_all_tables()
            >>> print(f"Found {len(tables)} tables")
        """
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)

            tables = [table[0] for table in cur.fetchall()]
            cur.close()
            return tables

        except Exception as e:
            print(f"[ERROR] Failed to retrieve tables: {e}")
            return None

    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a table.

        Args:
            table_name (str): Table to inspect

        Returns:
            dict or None: Dictionary with table information

        Example:
            >>> info = loader.get_table_info("users")
            >>> print(info['columns'])
        """
        if not table_name:
            print("[ERROR] Table name cannot be empty.")
            return None

        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            # Get column information
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))

            columns = []
            for col in cur.fetchall():
                columns.append({
                    'name': col[0],
                    'type': col[1],
                    'nullable': col[2] == 'YES',
                    'default': col[3]
                })

            # Get row count
            cur.execute(f'SELECT COUNT(*) FROM {table_name};')
            row_count = cur.fetchone()[0]

            cur.close()

            return {
                'table_name': table_name,
                'columns': columns,
                'row_count': row_count
            }

        except Exception as e:
            print(f"[ERROR] Failed to get table info: {e}")
            return None

    def query_to_dataframe(self, query: str, params: tuple = None) -> Optional[pd.DataFrame]:
        """
        Execute SQL query and return results as DataFrame.

        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters for safe parameterization

        Returns:
            pd.DataFrame or None: Query results as DataFrame

        Example:
            >>> df = loader.query_to_dataframe("SELECT * FROM users WHERE age > %s", (25,))
        """
        conn = None
        try:
            conn = self.get_connection()
            df = pd.read_sql_query(query, conn, params=params)
            return df
        except Exception as e:
            print(f"[ERROR] Query execution failed: {e}")
            return None

    def table_to_dataframe(self, table_name: str, limit: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Load entire table or top N rows into DataFrame.

        Args:
            table_name (str): Table to load
            limit (int, optional): Maximum rows to load (None = all rows)

        Returns:
            pd.DataFrame or None: Table data as DataFrame

        Example:
            >>> df = loader.table_to_dataframe("users", limit=100)
        """
        if not table_name:
            print("[ERROR] Table name cannot be empty.")
            return None

        limit_clause = f"LIMIT {limit}" if limit else ""
        query = f'SELECT * FROM {table_name} {limit_clause};'

        return self.query_to_dataframe(query)

    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists in database.

        Args:
            table_name (str): Table name to check

        Returns:
            bool: True if table exists, False otherwise

        Example:
            >>> if loader.table_exists("users"):
            ...     print("Table exists!")
        """
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                );
            """, (table_name,))

            exists = cur.fetchone()[0]
            cur.close()
            return exists

        except Exception as e:
            print(f"[ERROR] Failed to check table existence: {e}")
            return False

    def __repr__(self):
        """String representation of the loader instance."""
        return (f"PostgreSQLDataLoader(host='{self.host}', port='{self.port}', "
                f"database='{self.database}', user='{self.user}')")


# Backward compatibility: Provide standalone functions that use the class
def create_table_from_dataframe(df: pd.DataFrame, table_name: str,
                               primary_key: Optional[str] = None,
                               host: str = None, port: str = None,
                               database: str = None, user: str = None,
                               password: str = None) -> bool:
    """Standalone function for backward compatibility."""
    loader = PostgreSQLDataLoader(host, port, database, user, password)
    return loader.create_table_from_dataframe(df, table_name, primary_key)


def insert_dataframe_to_table(df: pd.DataFrame, table_name: str) -> Optional[int]:
    """Standalone function for backward compatibility."""
    loader = PostgreSQLDataLoader()
    return loader.insert_dataframe(df, table_name)


def drop_table(table_name: str, cascade: bool = False,
              host: str = None, port: str = None,
              database: str = None, user: str = None,
              password: str = None) -> bool:
    """Standalone function for backward compatibility."""
    loader = PostgreSQLDataLoader(host, port, database, user, password)
    return loader.drop_table(table_name, cascade)


def clear_table_data(table_name: str):
    """Standalone function for backward compatibility."""
    loader = PostgreSQLDataLoader()
    return loader.truncate_table(table_name)


def print_all_table_names():
    """Standalone function for backward compatibility."""
    loader = PostgreSQLDataLoader()
    tables = loader.get_all_tables()
    if tables:
        print(f"\nFound {len(tables)} tables:")
        print("-" * 40)
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        print("-" * 40)


def print_table_columns(table_name: str):
    """Standalone function for backward compatibility."""
    loader = PostgreSQLDataLoader()
    info = loader.get_table_info(table_name)
    if info:
        print(f"\nTable: {table_name}")
        print("=" * 60)
        print(f"{'Column Name':<25} | {'Data Type':<15} | {'Nullable':<8}")
        print("-" * 60)
        for col in info['columns']:
            nullable = "YES" if col['nullable'] else "NO"
            print(f"{col['name']:<25} | {col['type']:<15} | {nullable:<8}")
        print("=" * 60)


def get_table_column_names(table_name: str) -> Optional[List[str]]:
    """Standalone function for backward compatibility."""
    loader = PostgreSQLDataLoader()
    info = loader.get_table_info(table_name)
    return [col['name'] for col in info['columns']] if info else None


def select_top_n_rows(table_name: str, limit: int = 5) -> Optional[List[Tuple]]:
    """Standalone function for backward compatibility."""
    loader = PostgreSQLDataLoader()
    df = loader.table_to_dataframe(table_name, limit=limit)
    if df is not None:
        print(f"\nTop {len(df)} rows from '{table_name}':")
        print("=" * 70)
        print(df)
        print("=" * 70)
        return [tuple(row) for row in df.values]
    return None


def get_connection(host: str = None, port: str = None, database: str = None,
                  user: str = None, password: str = None):
    """Standalone function for backward compatibility."""
    loader = PostgreSQLDataLoader(host, port, database, user, password)
    try:
        return loader.get_connection()
    except:
        return None


# Module metadata
__version__ = '1.0.0'
__author__ = 'PostgreSQL DataLoader Contributors'
__license__ = 'MIT'
