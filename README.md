# PostgreSQL DataLoader 🐘

A comprehensive Python toolkit for seamless PostgreSQL database operations with pandas DataFrame integration. Load CSV files, create tables, manage data, and explore your database with ease!

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-12%2B-blue)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Easy Database Operations**
- 🔌 Connect to any PostgreSQL database with flexible credentials
- 📊 Automatically create tables from pandas DataFrames
- 📥 Bulk insert DataFrame data with validation
- 🗑️ Drop tables with CASCADE support
- 🧹 Clear table data while preserving structure

✨ **Smart Data Handling**
- 🔄 Automatic data type mapping (pandas → PostgreSQL)
- 📏 Handles column names with spaces and special characters
- 🔢 Cleans numeric data (removes commas automatically)
- ✅ Data type validation before insertion
- 📝 Supports columns exceeding PostgreSQL's 63-character limit

✨ **Database Exploration**
- 📋 List all tables in database
- 🔍 Inspect table schemas and column details
- 📖 Query and preview table data
- 📈 Get column names and metadata

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Sample Data](#sample-data)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.7 or higher
- PostgreSQL 12 or higher
- pip package manager

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Manual Installation

```bash
pip install psycopg2-binary pandas python-dotenv
```

## Quick Start

### 1. Configure Database Connection

Edit the connection details in `src/postgresql_dataloader.py`:

```python
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "your_database"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
```

Or use environment variables (recommended for security):

```bash
# Create .env file
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

### 2. Load CSV Data into PostgreSQL

```python
import pandas as pd
from src.postgresql_dataloader import (
    create_table_from_dataframe,
    insert_dataframe_to_table
)

# Read CSV file
df = pd.read_csv('data/sample_customer_demographics.csv')

# Create table from DataFrame schema
create_table_from_dataframe(df, "customers")

# Insert data
insert_dataframe_to_table(df, "customers")
```

### 3. Explore Your Database

```python
from src.postgresql_dataloader import (
    print_all_table_names,
    print_table_columns,
    select_top_n_rows
)

# List all tables
print_all_table_names()

# View table structure
print_table_columns("customers")

# Preview data
select_top_n_rows("customers", limit=10)
```

## Usage Examples

### Example 1: Complete CSV to Database Workflow

```python
import pandas as pd
from src.postgresql_dataloader import *

# Load CSV
df = pd.read_csv('data/sample_customer_transactions.csv')

# Clean numeric columns (remove commas)
df['WITHDRAW'] = df['WITHDRAW'].str.replace(',', '').astype(float)
df['DEPOSIT'] = df['DEPOSIT'].str.replace(',', '').astype(float)
df['BALANCE'] = df['BALANCE'].str.replace(',', '').astype(float)

# Create and populate table
create_table_from_dataframe(df, "transactions", primary_key="Customer ID")
rows_inserted = insert_dataframe_to_dataframe(df, "transactions")

print(f"Successfully inserted {rows_inserted} rows!")
```

### Example 2: Connect to Custom Database

```python
from src.postgresql_dataloader import get_connection

# Connect to specific database
conn = get_connection(
    host="my-server.com",
    port="5432",
    database="production_db",
    user="admin",
    password="secure_password"
)

if conn:
    print("Connected successfully!")
    conn.close()
```

### Example 3: Data Type Mapping

The module automatically maps pandas data types to PostgreSQL:

| Pandas Type | PostgreSQL Type |
|-------------|-----------------|
| int64       | INTEGER         |
| float64     | DOUBLE PRECISION|
| bool        | BOOLEAN         |
| datetime64  | TIMESTAMP       |
| object/str  | TEXT            |

```python
import pandas as pd
from src.postgresql_dataloader import create_table_from_dataframe

df = pd.DataFrame({
    'id': [1, 2, 3],                    # → INTEGER
    'name': ['Alice', 'Bob', 'Charlie'], # → TEXT
    'age': [25, 30, 35],                # → INTEGER
    'salary': [50000.0, 60000.0, 70000.0], # → DOUBLE PRECISION
    'is_active': [True, True, False]    # → BOOLEAN
})

create_table_from_dataframe(df, "employees", primary_key="id")
```

### Example 4: Table Management

```python
from src.postgresql_dataloader import (
    clear_table_data,
    drop_table
)

# Remove all data but keep table structure
clear_table_data("old_transactions")

# Drop table completely
drop_table("obsolete_table", cascade=True)
```

## API Reference

### Connection Management

#### `get_connection(host=None, port=None, database=None, user=None, password=None)`
Creates a PostgreSQL connection.

**Returns:** Connection object or None

### Table Operations

#### `create_table_from_dataframe(df, table_name, primary_key=None, **connection_params)`
Creates a table based on DataFrame schema.

**Parameters:**
- `df` (DataFrame): Source DataFrame
- `table_name` (str): Name of table to create
- `primary_key` (str, optional): Column to set as primary key
- `**connection_params`: Optional host, port, database, user, password

**Returns:** Boolean (True if successful)

#### `insert_dataframe_to_table(df, table_name)`
Inserts DataFrame rows into existing table.

**Parameters:**
- `df` (DataFrame): Data to insert
- `table_name` (str): Target table name

**Returns:** Number of rows inserted or None

#### `drop_table(table_name, cascade=False, **connection_params)`
Drops a table from the database.

**Parameters:**
- `table_name` (str): Table to drop
- `cascade` (bool): If True, drops dependent objects
- `**connection_params`: Optional connection parameters

**Returns:** Boolean (True if successful)

#### `clear_table_data(table_name)`
Truncates table (removes all rows, resets sequences).

**Parameters:**
- `table_name` (str): Table to truncate

### Exploration Functions

#### `print_all_table_names()`
Lists all tables in the database.

#### `print_table_columns(table_name)`
Displays column details for a table.

**Parameters:**
- `table_name` (str): Table to inspect

#### `get_table_column_names(table_name)`
Returns list of column names.

**Parameters:**
- `table_name` (str): Table name

**Returns:** List of column names

#### `select_top_n_rows(table_name, limit=5)`
Queries and displays top N rows.

**Parameters:**
- `table_name` (str): Table to query
- `limit` (int): Number of rows to retrieve

**Returns:** List of tuples containing row data

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=my_database
DB_USER=postgres
DB_PASSWORD=your_secure_password
```

### Database Connection Settings

Default settings in `src/postgresql_dataloader.py`:

```python
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "bbl_ai_lab_aml"
DB_USER = "postgres"
DB_PASSWORD = "post2346"
```

**🔒 Security Note:** For production, always use environment variables or secure credential management instead of hardcoding passwords.

## Sample Data

The `data/` folder contains sample CSV files for testing:

### sample_customer_demographics.csv
Sample customer account information (10 rows)
- Account details
- Customer information
- Risk ratings
- Contact information

### sample_customer_transactions.csv
Sample transaction records (50 rows)
- Transaction dates and amounts
- Withdrawal and deposit information
- Transaction types and details

## Project Structure

```
PostgreSQL_DataLoader/
├── data/
│   ├── sample_customer_demographics.csv
│   └── sample_customer_transactions.csv
├── src/
│   └── postgresql_dataloader.py
├── examples/
│   ├── basic_usage.py
│   └── advanced_operations.py
├── docs/
│   └── API_DOCUMENTATION.md
├── .gitignore
├── .env.example
├── requirements.txt
├── LICENSE
└── README.md
```

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'psycopg2'`
**Solution:** Install psycopg2: `pip install psycopg2-binary`

**Issue:** `OperationalError: could not connect to server`
**Solution:** Verify PostgreSQL is running and connection credentials are correct

**Issue:** `SyntaxError: syntax error at or near "Date"`
**Solution:** Column names with spaces are automatically quoted by the module

**Issue:** Column name truncation
**Solution:** PostgreSQL limits identifiers to 63 characters. The module handles this automatically.

## Performance Tips

- Use `page_size=1000` for bulk inserts (default in module)
- Create indexes after data insertion for better performance
- Use `TRUNCATE` (via `clear_table_data()`) instead of `DELETE` for clearing large tables
- Consider batching very large CSV files

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/postgresql-dataloader.git

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [psycopg2](https://www.psycopg.org/) - PostgreSQL adapter for Python
- Powered by [pandas](https://pandas.pydata.org/) - Data analysis library
- Uses [python-dotenv](https://github.com/theskumar/python-dotenv) for environment management

## Support

If you encounter any issues or have questions:

- 📫 Open an issue on GitHub
- 📖 Check the [documentation](docs/API_DOCUMENTATION.md)
- 💬 Join our discussions

## Roadmap

- [ ] Add support for more complex data types (JSON, arrays)
- [ ] Implement query builder
- [ ] Add data migration tools
- [ ] Support for multiple database connections
- [ ] CLI tool for quick operations
- [ ] Docker containerization
- [ ] Unit tests and CI/CD pipeline

---

**Made with ❤️ for the PostgreSQL and Python community**

⭐ Star this repo if you find it helpful!
