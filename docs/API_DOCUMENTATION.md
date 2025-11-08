# API Documentation

Complete reference for all functions in the PostgreSQL DataLoader module.

## Table of Contents

- [Connection Management](#connection-management)
- [Table Creation](#table-creation)
- [Data Insertion](#data-insertion)
- [Table Management](#table-management)
- [Database Exploration](#database-exploration)
- [Utility Functions](#utility-functions)

---

## Connection Management

### `get_connection()`

Creates and returns a PostgreSQL database connection.

**Signature:**
```python
get_connection(
    host: str = None,
    port: str = None,
    database: str = None,
    user: str = None,
    password: str = None
) -> psycopg2.connection
```

**Parameters:**
- `host` (str, optional): Database host address. Defaults to DB_HOST constant.
- `port` (str, optional): Database port number. Defaults to DB_PORT constant.
- `database` (str, optional): Database name. Defaults to DB_NAME constant.
- `user` (str, optional): Database username. Defaults to DB_USER constant.
- `password` (str, optional): Database password. Defaults to DB_PASSWORD constant.

**Returns:**
- `psycopg2.connection` or `None`: Connection object if successful, None if failed.

**Example:**
```python
# Use default connection
conn = get_connection()

# Custom connection
conn = get_connection(
    host="myserver.com",
    database="production",
    user="admin",
    password="secret"
)

if conn:
    print("Connected!")
    conn.close()
```

---

## Table Creation

### `create_table_from_dataframe()`

Creates a PostgreSQL table based on a pandas DataFrame schema.

**Signature:**
```python
create_table_from_dataframe(
    df: pd.DataFrame,
    table_name: str,
    primary_key: Optional[str] = None,
    host: str = None,
    port: str = None,
    database: str = None,
    user: str = None,
    password: str = None
) -> bool
```

**Parameters:**
- `df` (pd.DataFrame): DataFrame whose schema defines the table structure.
- `table_name` (str): Name of the table to create.
- `primary_key` (str, optional): Column name to set as primary key.
- `host`, `port`, `database`, `user`, `password` (str, optional): Connection parameters.

**Returns:**
- `bool`: True if successful, False otherwise.

**Data Type Mapping:**
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

df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000.0, 60000.0, 70000.0]
})

# Create table with primary key
success = create_table_from_dataframe(
    df=df,
    table_name="employees",
    primary_key="id"
)
```

**Notes:**
- Uses `CREATE TABLE IF NOT EXISTS` - won't fail if table exists
- Column names with spaces are automatically quoted
- Long column names (>63 chars) are truncated by PostgreSQL

---

## Data Insertion

### `insert_dataframe_to_table()`

Inserts DataFrame rows into an existing PostgreSQL table with validation.

**Signature:**
```python
insert_dataframe_to_table(
    df: pd.DataFrame,
    table_name: str
) -> Optional[int]
```

**Parameters:**
- `df` (pd.DataFrame): DataFrame containing data to insert.
- `table_name` (str): Target table name.

**Returns:**
- `int` or `None`: Number of rows inserted, or None if failed.

**Features:**
- Validates DataFrame columns match table schema
- Performs data type validation
- Uses bulk insert with page_size=1000 for efficiency
- Automatic rollback on errors
- Handles column names with spaces

**Example:**
```python
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000.0, 60000.0, 70000.0]
})

# Table must exist first
create_table_from_dataframe(df, "employees", primary_key="id")

# Insert data
rows_inserted = insert_dataframe_to_table(df, "employees")
print(f"Inserted {rows_inserted} rows")
```

**Error Handling:**
- Returns None if table doesn't exist
- Returns None if DataFrame columns don't match table
- Returns None if data type validation fails
- Automatic transaction rollback on errors

---

## Table Management

### `drop_table()`

Drops (deletes) a PostgreSQL table.

**Signature:**
```python
drop_table(
    table_name: str,
    cascade: bool = False,
    host: str = None,
    port: str = None,
    database: str = None,
    user: str = None,
    password: str = None
) -> bool
```

**Parameters:**
- `table_name` (str): Name of the table to drop.
- `cascade` (bool, optional): If True, drops dependent objects. Default: False.
- Connection parameters (optional).

**Returns:**
- `bool`: True if successful, False otherwise.

**Example:**
```python
# Drop table without cascade
drop_table("old_data")

# Drop table and all dependent objects
drop_table("parent_table", cascade=True)

# Drop from specific database
drop_table(
    "temp_table",
    host="other-server",
    database="test_db"
)
```

**SQL Generated:**
- Without cascade: `DROP TABLE IF EXISTS table_name RESTRICT;`
- With cascade: `DROP TABLE IF EXISTS table_name CASCADE;`

---

### `clear_table_data()`

Truncates a table (removes all rows, resets sequences).

**Signature:**
```python
clear_table_data(table_name: str) -> None
```

**Parameters:**
- `table_name` (str): Table to truncate.

**Returns:**
- None

**Example:**
```python
# Remove all data but keep table structure
clear_table_data("temporary_data")
```

**SQL Generated:**
```sql
TRUNCATE TABLE table_name RESTART IDENTITY CASCADE;
```

**Features:**
- Resets auto-increment sequences
- Cascades to dependent tables
- Much faster than DELETE for large tables
- Cannot be rolled back

---

## Database Exploration

### `print_all_table_names()`

Lists all user-defined tables in the database.

**Signature:**
```python
print_all_table_names() -> None
```

**Parameters:**
- None

**Returns:**
- None (prints to console)

**Example:**
```python
print_all_table_names()
# Output:
# ✅ Found 5 tables in database 'mydb':
# ------------------------------
# 1. customers
# 2. orders
# 3. products
# 4. employees
# 5. transactions
# ------------------------------
```

---

### `print_table_columns()`

Displays column details for a specified table.

**Signature:**
```python
print_table_columns(table_name: str) -> None
```

**Parameters:**
- `table_name` (str): Table to inspect.

**Returns:**
- None (prints to console)

**Example:**
```python
print_table_columns("employees")
# Output:
# ✅ Columns found in table 'employees':
# ============================================================
# Column Name          | Data Type        | Nullable
# ------------------------------------------------------------
# id                   | integer          | NO
# name                 | text             | YES
# age                  | integer          | YES
# salary               | double precision | YES
# ============================================================
```

---

### `get_table_column_names()`

Returns a list of column names for a table.

**Signature:**
```python
get_table_column_names(table_name: str) -> Optional[List[str]]
```

**Parameters:**
- `table_name` (str): Table name.

**Returns:**
- `List[str]` or `None`: List of column names, or None if error.

**Example:**
```python
columns = get_table_column_names("employees")
print(columns)
# Output: ['id', 'name', 'age', 'salary']
```

---

### `select_top_n_rows()`

Retrieves and displays the first N rows from a table.

**Signature:**
```python
select_top_n_rows(
    table_name: str,
    limit: int = 5
) -> Optional[List[Tuple]]
```

**Parameters:**
- `table_name` (str): Table to query.
- `limit` (int, optional): Number of rows to retrieve. Default: 5.

**Returns:**
- `List[Tuple]` or `None`: List of row tuples, or None if error.

**Example:**
```python
rows = select_top_n_rows("employees", limit=3)
# Prints results and returns them

# Access returned data
for row in rows:
    print(row)
```

---

## Utility Functions

### `compare_lists()`

Compares two lists and returns missing elements from each.

**Signature:**
```python
compare_lists(list1: list, list2: list) -> dict
```

**Parameters:**
- `list1` (list): First list.
- `list2` (list): Second list.

**Returns:**
- `dict`: Dictionary with 'missing_in_list1' and 'missing_in_list2'.

**Example:**
```python
result = compare_lists(['a', 'b', 'c'], ['b', 'c', 'd'])
print(result)
# Output: {
#     'missing_in_list1': ['d'],
#     'missing_in_list2': ['a']
# }
```

---

## Error Handling

All functions include comprehensive error handling:

### Connection Errors
```python
try:
    conn = get_connection()
except OperationalError as e:
    print(f"Connection failed: {e}")
```

### Table Operations
```python
success = create_table_from_dataframe(df, "mytable")
if not success:
    print("Table creation failed")
```

### Data Insertion
```python
rows = insert_dataframe_to_table(df, "mytable")
if rows is None:
    print("Insert failed")
else:
    print(f"Inserted {rows} rows")
```

---

## Best Practices

1. **Always check return values**
   ```python
   if create_table_from_dataframe(df, "mytable"):
       insert_dataframe_to_table(df, "mytable")
   ```

2. **Use environment variables for credentials**
   ```python
   # Don't hardcode passwords!
   # Use .env file instead
   ```

3. **Handle long column names**
   ```python
   # Rename columns > 63 characters before creating table
   df.rename(columns={'very_long_column_name...': 'short_name'})
   ```

4. **Clean numeric data**
   ```python
   # Remove commas from numbers
   df['amount'] = df['amount'].str.replace(',', '').astype(float)
   ```

5. **Close connections**
   ```python
   conn = get_connection()
   try:
       # Do work
       pass
   finally:
       if conn:
           conn.close()
   ```

---

## Performance Tips

- Bulk inserts use page_size=1000 by default
- Use `TRUNCATE` (clear_table_data) instead of DELETE for large tables
- Create indexes after data insertion
- Consider batching very large datasets
- Use connection pooling for production applications

---

## Support

For issues, questions, or contributions:
- GitHub Issues: [Report a bug](https://github.com/yourusername/postgresql-dataloader/issues)
- Documentation: [Main README](../README.md)
