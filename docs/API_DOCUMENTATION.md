# API Documentation

Complete reference for the PostgreSQL DataLoader module.

## Table of Contents

- [PostgreSQLDataLoader Class (Recommended)](#postgresqldataloader-class-recommended)
  - [Initialization](#initialization)
  - [Context Manager Support](#context-manager-support)
  - [Table Operations](#table-operations)
  - [Data Operations](#data-operations)
  - [Query Operations](#query-operations)
  - [Database Exploration](#database-exploration)
- [Legacy Function-Based API](#legacy-function-based-api)
- [Data Type Mapping](#data-type-mapping)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

---

## PostgreSQLDataLoader Class (Recommended)

The `PostgreSQLDataLoader` class provides a modern, object-oriented interface for PostgreSQL operations with pandas DataFrame integration.

### Initialization

#### `PostgreSQLDataLoader(host=None, port=None, database=None, user=None, password=None)`

Creates a new PostgreSQLDataLoader instance.

**Signature:**
```python
PostgreSQLDataLoader(
    host: str = None,
    port: str = None,
    database: str = None,
    user: str = None,
    password: str = None
)
```

**Parameters:**
- `host` (str, optional): Database host address. Defaults to environment variable `DB_HOST` or 'localhost'.
- `port` (str, optional): Database port number. Defaults to environment variable `DB_PORT` or '5432'.
- `database` (str, optional): Database name. Defaults to environment variable `DB_NAME`.
- `user` (str, optional): Database username. Defaults to environment variable `DB_USER`.
- `password` (str, optional): Database password. Defaults to environment variable `DB_PASSWORD`.

**Example:**
```python
from src.postgresql_dataloader import PostgreSQLDataLoader

# Use default connection (from .env file)
loader = PostgreSQLDataLoader()

# Custom connection
loader = PostgreSQLDataLoader(
    host="myserver.com",
    port="5432",
    database="production",
    user="admin",
    password="secret"
)
```

### Context Manager Support

The class supports Python's context manager protocol for automatic connection management.

**Example:**
```python
# Automatic connection handling
with PostgreSQLDataLoader() as loader:
    loader.create_table_from_dataframe(df, "mytable")
    loader.insert_dataframe(df, "mytable")
# Connection automatically closed here
```

---

### Table Operations

#### `create_table_from_dataframe(df, table_name, primary_key=None, if_exists='skip')`

Creates a PostgreSQL table based on a pandas DataFrame schema.

**Signature:**
```python
loader.create_table_from_dataframe(
    df: pd.DataFrame,
    table_name: str,
    primary_key: Optional[str] = None,
    if_exists: str = 'skip'
) -> bool
```

**Parameters:**
- `df` (pd.DataFrame): DataFrame whose schema defines the table structure.
- `table_name` (str): Name of the table to create.
- `primary_key` (str, optional): Column name to set as primary key.
- `if_exists` (str, optional): Action if table exists: 'skip', 'replace', 'fail'. Default: 'skip'.

**Returns:**
- `bool`: True if successful, False otherwise.

**Example:**
```python
import pandas as pd
from src.postgresql_dataloader import PostgreSQLDataLoader

df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000.0, 60000.0, 70000.0]
})

with PostgreSQLDataLoader() as loader:
    # Create table with primary key
    loader.create_table_from_dataframe(
        df=df,
        table_name="employees",
        primary_key="id"
    )

    # Replace existing table
    loader.create_table_from_dataframe(
        df=df,
        table_name="employees",
        if_exists="replace"
    )
```

**Notes:**
- Column names with spaces are automatically quoted
- Long column names (>63 chars) are truncated by PostgreSQL
- Automatic data type mapping from pandas to PostgreSQL

---

#### `drop_table(table_name, cascade=False)`

Drops (deletes) a PostgreSQL table.

**Signature:**
```python
loader.drop_table(
    table_name: str,
    cascade: bool = False
) -> bool
```

**Parameters:**
- `table_name` (str): Name of the table to drop.
- `cascade` (bool, optional): If True, drops dependent objects. Default: False.

**Returns:**
- `bool`: True if successful, False otherwise.

**Example:**
```python
with PostgreSQLDataLoader() as loader:
    # Drop table without cascade
    loader.drop_table("old_data")

    # Drop table and all dependent objects
    loader.drop_table("parent_table", cascade=True)
```

**SQL Generated:**
- Without cascade: `DROP TABLE IF EXISTS table_name RESTRICT;`
- With cascade: `DROP TABLE IF EXISTS table_name CASCADE;`

---

#### `truncate_table(table_name)`

Truncates a table (removes all rows, resets sequences).

**Signature:**
```python
loader.truncate_table(table_name: str) -> bool
```

**Parameters:**
- `table_name` (str): Table to truncate.

**Returns:**
- `bool`: True if successful, False otherwise.

**Example:**
```python
with PostgreSQLDataLoader() as loader:
    # Remove all data but keep table structure
    loader.truncate_table("temporary_data")
```

**Features:**
- Resets auto-increment sequences
- Cascades to dependent tables
- Much faster than DELETE for large tables
- Cannot be rolled back

---

#### `table_exists(table_name)`

Check if a table exists in the database.

**Signature:**
```python
loader.table_exists(table_name: str) -> bool
```

**Parameters:**
- `table_name` (str): Table name to check.

**Returns:**
- `bool`: True if table exists, False otherwise.

**Example:**
```python
with PostgreSQLDataLoader() as loader:
    if loader.table_exists("customers"):
        print("Table exists!")
    else:
        print("Table does not exist")
```

---

### Data Operations

#### `insert_dataframe(df, table_name, batch_size=1000)`

Inserts DataFrame rows into an existing PostgreSQL table with validation.

**Signature:**
```python
loader.insert_dataframe(
    df: pd.DataFrame,
    table_name: str,
    batch_size: int = 1000
) -> Optional[int]
```

**Parameters:**
- `df` (pd.DataFrame): DataFrame containing data to insert.
- `table_name` (str): Target table name.
- `batch_size` (int, optional): Number of rows per batch. Default: 1000.

**Returns:**
- `int` or `None`: Number of rows inserted, or None if failed.

**Features:**
- Validates DataFrame columns match table schema
- Performs data type validation
- Configurable batch size for bulk inserts
- Automatic rollback on errors
- Handles column names with spaces

**Example:**
```python
import pandas as pd
from src.postgresql_dataloader import PostgreSQLDataLoader

df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000.0, 60000.0, 70000.0]
})

with PostgreSQLDataLoader() as loader:
    # Table must exist first
    loader.create_table_from_dataframe(df, "employees", primary_key="id")

    # Insert data with default batch size
    rows = loader.insert_dataframe(df, "employees")
    print(f"Inserted {rows} rows")

    # Insert with custom batch size
    rows = loader.insert_dataframe(df, "employees", batch_size=500)
```

**Error Handling:**
- Returns None if table doesn't exist
- Returns None if DataFrame columns don't match table
- Returns None if data type validation fails
- Automatic transaction rollback on errors

---

### Query Operations

#### `table_to_dataframe(table_name, limit=None)`

Load table data into a pandas DataFrame.

**Signature:**
```python
loader.table_to_dataframe(
    table_name: str,
    limit: Optional[int] = None
) -> Optional[pd.DataFrame]
```

**Parameters:**
- `table_name` (str): Table to query.
- `limit` (int, optional): Number of rows to retrieve. If None, retrieves all rows.

**Returns:**
- `pd.DataFrame` or `None`: DataFrame with table data, or None if failed.

**Example:**
```python
with PostgreSQLDataLoader() as loader:
    # Load all rows
    df = loader.table_to_dataframe("employees")

    # Load first 10 rows
    df = loader.table_to_dataframe("employees", limit=10)

    print(df.head())
```

---

#### `query_to_dataframe(query, params=None)`

Execute custom SQL query and return DataFrame.

**Signature:**
```python
loader.query_to_dataframe(
    query: str,
    params: tuple = None
) -> Optional[pd.DataFrame]
```

**Parameters:**
- `query` (str): SQL query to execute.
- `params` (tuple, optional): Query parameters for parameterized queries.

**Returns:**
- `pd.DataFrame` or `None`: DataFrame with query results, or None if failed.

**Example:**
```python
with PostgreSQLDataLoader() as loader:
    # Simple query
    df = loader.query_to_dataframe("SELECT * FROM employees WHERE age > 25")

    # Parameterized query (prevents SQL injection)
    df = loader.query_to_dataframe(
        "SELECT * FROM employees WHERE age > %s AND salary > %s",
        params=(25, 50000)
    )

    print(df)
```

**Note:** Always use parameterized queries when using user input to prevent SQL injection.

---

### Database Exploration

#### `get_all_tables()`

Returns a list of all user-defined tables in the database.

**Signature:**
```python
loader.get_all_tables() -> List[str]
```

**Parameters:**
- None

**Returns:**
- `List[str]`: List of table names.

**Example:**
```python
with PostgreSQLDataLoader() as loader:
    tables = loader.get_all_tables()
    print(f"Found {len(tables)} tables: {tables}")
    # Output: Found 5 tables: ['customers', 'orders', 'products', 'employees', 'transactions']
```

---

#### `get_table_info(table_name)`

Get detailed table metadata including columns and types.

**Signature:**
```python
loader.get_table_info(table_name: str) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `table_name` (str): Table to inspect.

**Returns:**
- `Dict` or `None`: Dictionary with table information, or None if table doesn't exist.

**Return Structure:**
```python
{
    'name': 'employees',
    'columns': [
        {'name': 'id', 'type': 'integer', 'nullable': False},
        {'name': 'name', 'type': 'text', 'nullable': True},
        {'name': 'age', 'type': 'integer', 'nullable': True},
        {'name': 'salary', 'type': 'double precision', 'nullable': True}
    ]
}
```

**Example:**
```python
with PostgreSQLDataLoader() as loader:
    info = loader.get_table_info("employees")
    if info:
        print(f"Table: {info['name']}")
        for col in info['columns']:
            print(f"  {col['name']}: {col['type']} ({'NULL' if col['nullable'] else 'NOT NULL'})")
```

---

## Legacy Function-Based API

For backward compatibility, the module provides standalone functions that work without instantiating the class. These functions internally create a `PostgreSQLDataLoader` instance.

### Available Legacy Functions

- `get_connection(host, port, database, user, password)` - Create database connection
- `create_table_from_dataframe(df, table_name, primary_key, **connection_params)` - Create table
- `insert_dataframe_to_table(df, table_name)` - Insert data
- `drop_table(table_name, cascade, **connection_params)` - Drop table
- `clear_table_data(table_name)` - Truncate table
- `print_all_table_names()` - Print all tables
- `print_table_columns(table_name)` - Print table columns
- `get_table_column_names(table_name)` - Get column names list
- `select_top_n_rows(table_name, limit)` - Query and print rows

**Example:**
```python
from src.postgresql_dataloader import (
    create_table_from_dataframe,
    insert_dataframe_to_table,
    print_all_table_names
)

# Use legacy functions (not recommended for new code)
create_table_from_dataframe(df, "employees", primary_key="id")
insert_dataframe_to_table(df, "employees")
print_all_table_names()
```

**Note:** The class-based API is recommended for new code as it provides better resource management and additional features.

---

## Data Type Mapping

The module automatically maps pandas data types to PostgreSQL types:

| Pandas Type | PostgreSQL Type  |
|-------------|------------------|
| int64       | INTEGER          |
| float64     | DOUBLE PRECISION |
| bool        | BOOLEAN          |
| datetime64  | TIMESTAMP        |
| date        | DATE             |
| object/str  | TEXT             |

**Example:**
```python
import pandas as pd
from src.postgresql_dataloader import PostgreSQLDataLoader

df = pd.DataFrame({
    'id': [1, 2],                    # → INTEGER
    'name': ['Alice', 'Bob'],        # → TEXT
    'salary': [50000.0, 60000.0],    # → DOUBLE PRECISION
    'is_active': [True, False],      # → BOOLEAN
    'hired': pd.to_datetime(['2020-01-15', '2019-05-20'])  # → TIMESTAMP
})

with PostgreSQLDataLoader() as loader:
    loader.create_table_from_dataframe(df, "employees")
```

---

## Error Handling

All methods include comprehensive error handling with clear return values.

### Connection Errors
```python
from src.postgresql_dataloader import PostgreSQLDataLoader

try:
    with PostgreSQLDataLoader(host="invalid-host") as loader:
        tables = loader.get_all_tables()
except Exception as e:
    print(f"Connection failed: {e}")
```

### Table Operations
```python
with PostgreSQLDataLoader() as loader:
    success = loader.create_table_from_dataframe(df, "mytable")
    if not success:
        print("Table creation failed")
```

### Data Insertion
```python
with PostgreSQLDataLoader() as loader:
    rows = loader.insert_dataframe(df, "mytable")
    if rows is None:
        print("Insert failed - check that table exists and columns match")
    else:
        print(f"Successfully inserted {rows} rows")
```

### Checking Table Existence
```python
with PostgreSQLDataLoader() as loader:
    if loader.table_exists("mytable"):
        df = loader.table_to_dataframe("mytable")
    else:
        print("Table does not exist")
```

---

## Best Practices

### 1. Use Context Managers
Always use the `with` statement for automatic connection management:
```python
# Good - connection automatically closed
with PostgreSQLDataLoader() as loader:
    loader.create_table_from_dataframe(df, "mytable")
    loader.insert_dataframe(df, "mytable")

# Avoid - manual connection management
loader = PostgreSQLDataLoader()
loader.connect()
loader.create_table_from_dataframe(df, "mytable")
loader.disconnect()
```

### 2. Use Environment Variables for Credentials
Never hardcode passwords. Use a `.env` file:
```bash
# .env file
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=postgres
DB_PASSWORD=secret
```

```python
# Python code
from src.postgresql_dataloader import PostgreSQLDataLoader

# Automatically reads from .env
loader = PostgreSQLDataLoader()
```

### 3. Handle Long Column Names
PostgreSQL limits identifiers to 63 characters:
```python
# Rename long columns before creating table
column_mapping = {}
for col in df.columns:
    if len(col) > 63:
        column_mapping[col] = col[:63]

if column_mapping:
    df.rename(columns=column_mapping, inplace=True)
```

### 4. Clean Numeric Data
Remove commas and other formatting from numeric columns:
```python
# Clean before inserting
df['amount'] = df['amount'].str.replace(',', '').astype(float)
df['balance'] = df['balance'].str.replace('$', '').str.replace(',', '').astype(float)
```

### 5. Validate Data Before Insertion
```python
with PostgreSQLDataLoader() as loader:
    # Check if table exists
    if not loader.table_exists("mytable"):
        loader.create_table_from_dataframe(df, "mytable")

    # Get table info
    info = loader.get_table_info("mytable")
    if info:
        table_cols = [col['name'] for col in info['columns']]
        df_cols = df.columns.tolist()

        # Verify columns match
        if set(df_cols) == set(table_cols):
            loader.insert_dataframe(df, "mytable")
        else:
            print("Column mismatch!")
```

### 6. Use Batch Size for Large Datasets
```python
with PostgreSQLDataLoader() as loader:
    # Adjust batch size based on data complexity
    loader.insert_dataframe(large_df, "mytable", batch_size=500)
```

### 7. Use Parameterized Queries
```python
with PostgreSQLDataLoader() as loader:
    # Safe - prevents SQL injection
    df = loader.query_to_dataframe(
        "SELECT * FROM users WHERE age > %s",
        params=(25,)
    )

    # NEVER do this (vulnerable to SQL injection)
    # age = user_input
    # df = loader.query_to_dataframe(f"SELECT * FROM users WHERE age > {age}")
```

---

## Performance Tips

1. **Batch Size**: Default is 1000 rows per batch. Adjust based on your data:
   ```python
   loader.insert_dataframe(df, "mytable", batch_size=5000)  # For simple data
   loader.insert_dataframe(df, "mytable", batch_size=100)   # For complex data
   ```

2. **Use TRUNCATE**: Much faster than DELETE for clearing tables:
   ```python
   loader.truncate_table("mytable")  # Fast
   # vs
   loader.query_to_dataframe("DELETE FROM mytable")  # Slow
   ```

3. **Create Indexes After Insertion**: Insert data first, then create indexes:
   ```python
   with PostgreSQLDataLoader() as loader:
       loader.insert_dataframe(large_df, "mytable")
       # Then create indexes in psql or using query_to_dataframe
   ```

4. **Use Context Managers**: Reuse connection for multiple operations:
   ```python
   with PostgreSQLDataLoader() as loader:
       loader.create_table_from_dataframe(df1, "table1")
       loader.create_table_from_dataframe(df2, "table2")
       loader.insert_dataframe(df1, "table1")
       loader.insert_dataframe(df2, "table2")
   # Single connection for all operations
   ```

5. **Query Only What You Need**: Use `limit` parameter:
   ```python
   df = loader.table_to_dataframe("large_table", limit=1000)
   ```

---

## Complete Usage Example

Here's a comprehensive example combining all best practices:

```python
import pandas as pd
from src.postgresql_dataloader import PostgreSQLDataLoader

# Load and clean data
df = pd.read_csv('data.csv')

# Clean numeric columns
df['amount'] = df['amount'].str.replace(',', '').astype(float)

# Handle long column names
for col in df.columns:
    if len(col) > 63:
        new_name = col[:63]
        df.rename(columns={col: new_name}, inplace=True)

# Use context manager for all operations
with PostgreSQLDataLoader() as loader:
    # Check if table exists
    if loader.table_exists("transactions"):
        print("Table exists, truncating...")
        loader.truncate_table("transactions")
    else:
        print("Creating new table...")
        loader.create_table_from_dataframe(
            df,
            "transactions",
            primary_key="id"
        )

    # Insert data with appropriate batch size
    rows = loader.insert_dataframe(df, "transactions", batch_size=1000)
    print(f"Inserted {rows} rows")

    # Verify insertion
    result_df = loader.table_to_dataframe("transactions", limit=5)
    print("\nFirst 5 rows:")
    print(result_df)

    # Get table info
    info = loader.get_table_info("transactions")
    print(f"\nTable has {len(info['columns'])} columns")
```

---

## Support

For issues, questions, or contributions:
- **GitHub Issues**: [Report a bug](https://github.com/shahinvx/PostgreSQL_DataLoader/issues)
- **Main Documentation**: [README.md](../README.md)
- **Setup Guide**: [SETUP_GUIDE.md](../SETUP_GUIDE.md)

---

**Last Updated**: January 2025
**Module Version**: 1.0.0
