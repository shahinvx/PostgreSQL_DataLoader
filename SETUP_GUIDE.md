# Setup Guide - PostgreSQL DataLoader

Complete step-by-step guide to get PostgreSQL DataLoader running on your system.

## Prerequisites

### Required Software

1. **Python 3.7 or higher**
   - Download from: https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **PostgreSQL 12 or higher**
   - Download from: https://www.postgresql.org/download/
   - Verify installation: `psql --version`

3. **pip (Python package manager)**
   - Usually included with Python
   - Verify: `pip --version`

### Optional Tools

- **Git**: For cloning the repository
- **virtualenv** or **venv**: For isolated Python environments
- **pgAdmin** or **DBeaver**: For database management GUI

## Installation Steps

### Step 1: Download the Project

#### Option A: Clone with Git
```bash
git clone https://github.com/yourusername/postgresql-dataloader.git
cd postgresql-dataloader
```

#### Option B: Download ZIP
1. Download ZIP from GitHub
2. Extract to desired location
3. Open terminal in extracted folder

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `psycopg2-binary` - PostgreSQL adapter
- `pandas` - Data manipulation library
- `python-dotenv` - Environment variable management

### Step 4: Set Up PostgreSQL Database

#### Create a Database

```bash
# Using psql command line
createdb my_database

# Or using psql:
psql -U postgres
CREATE DATABASE my_database;
\q
```

#### Create Database User (Optional)

```bash
# Using psql
psql -U postgres
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE my_database TO myuser;
\q
```

### Step 5: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

Edit `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=my_database
DB_USER=postgres
DB_PASSWORD=your_password
```

### Step 6: Verify Installation

Run the basic example:

```bash
python examples/basic_usage.py
```

If everything is set up correctly, you should see tables being created and data being inserted.

## Platform-Specific Instructions

### Windows

1. **Install PostgreSQL**
   - Download installer from postgresql.org
   - Run installer and follow prompts
   - Remember your password for postgres user

2. **Add PostgreSQL to PATH**
   - Default location: `C:\Program Files\PostgreSQL\14\bin`
   - Add to System Environment Variables

3. **Install Python**
   - Download from python.org
   - Check "Add Python to PATH" during installation

4. **Open Command Prompt or PowerShell**
   ```powershell
   # Navigate to project folder
   cd C:\path\to\postgresql-dataloader

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

### macOS

1. **Install PostgreSQL**
   ```bash
   # Using Homebrew
   brew install postgresql
   brew services start postgresql
   ```

2. **Install Python** (if not already installed)
   ```bash
   # Using Homebrew
   brew install python
   ```

3. **Setup Project**
   ```bash
   # Navigate to project
   cd /path/to/postgresql-dataloader

   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

### Linux (Ubuntu/Debian)

1. **Install PostgreSQL**
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Install Python and pip**
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

3. **Setup Project**
   ```bash
   # Navigate to project
   cd /path/to/postgresql-dataloader

   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

## Quick Start Usage

### Example 1: Load Sample Data

```python
import pandas as pd
from src.postgresql_dataloader import (
    create_table_from_dataframe,
    insert_dataframe_to_table
)

# Read sample CSV
df = pd.read_csv('data/sample_customer_demographics.csv')

# Create table
create_table_from_dataframe(df, "customers")

# Insert data
insert_dataframe_to_table(df, "customers")
```

### Example 2: Explore Database

```python
from src.postgresql_dataloader import (
    print_all_table_names,
    print_table_columns,
    select_top_n_rows
)

# List tables
print_all_table_names()

# View table structure
print_table_columns("customers")

# Preview data
select_top_n_rows("customers", limit=5)
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "psycopg2" installation fails

**Error:**
```
ERROR: Could not build wheels for psycopg2
```

**Solution:**
```bash
# Install binary version instead
pip install psycopg2-binary
```

#### Issue 2: Cannot connect to PostgreSQL

**Error:**
```
OperationalError: could not connect to server
```

**Solutions:**
1. Verify PostgreSQL is running:
   ```bash
   # Windows
   pg_ctl status

   # macOS
   brew services list

   # Linux
   sudo systemctl status postgresql
   ```

2. Check connection settings in `.env`

3. Verify PostgreSQL is accepting connections:
   ```bash
   psql -U postgres -h localhost
   ```

#### Issue 3: Permission denied

**Error:**
```
FATAL: role "username" does not exist
```

**Solution:**
```bash
# Create the user in PostgreSQL
psql -U postgres
CREATE USER username WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE mydb TO username;
```

#### Issue 4: Module not found

**Error:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

#### Issue 5: Port already in use

**Error:**
```
Port 5432 already in use
```

**Solution:**
- Change PostgreSQL port in `postgresql.conf`
- Or update DB_PORT in `.env` to match

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| DB_HOST | Database host | localhost | Yes |
| DB_PORT | Database port | 5432 | Yes |
| DB_NAME | Database name | - | Yes |
| DB_USER | Database user | postgres | Yes |
| DB_PASSWORD | User password | - | Yes |

### Database Connection String

Alternatively, you can use a connection string:
```python
import psycopg2

conn_string = "postgresql://user:password@localhost:5432/database"
conn = psycopg2.connect(conn_string)
```

## Next Steps

1. ✅ **Run Examples**
   ```bash
   python examples/basic_usage.py
   python examples/advanced_operations.py
   ```

2. 📖 **Read Documentation**
   - [API Documentation](docs/API_DOCUMENTATION.md)
   - [README](README.md)

3. 🚀 **Start Your Project**
   - Load your own CSV files
   - Create custom database operations
   - Explore the API

4. 🤝 **Contribute**
   - Report bugs
   - Suggest features
   - Submit pull requests

## Getting Help

- **Documentation**: Check [README.md](README.md) and [docs/](docs/)
- **Examples**: See [examples/](examples/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/postgresql-dataloader/issues)
- **Community**: [GitHub Discussions](https://github.com/yourusername/postgresql-dataloader/discussions)

## Security Best Practices

1. **Never commit `.env` file to Git**
   - It's already in `.gitignore`
   - Use `.env.example` as template

2. **Use strong passwords**
   - Especially for production databases

3. **Limit database permissions**
   - Grant only necessary privileges

4. **Use SSL for remote connections**
   ```python
   conn = psycopg2.connect(
       host="remote-server",
       sslmode='require'
   )
   ```

## Uninstallation

### Remove Virtual Environment
```bash
# Deactivate first
deactivate

# Remove venv folder
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```

### Remove Database
```bash
# Using psql
dropdb my_database

# Or in psql:
DROP DATABASE my_database;
```

---

**Ready to start?** Run `python examples/basic_usage.py` to see it in action!
