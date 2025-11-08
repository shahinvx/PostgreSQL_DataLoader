"""
Advanced Operations for PostgreSQL DataLoader

This script demonstrates advanced features:
1. Custom database connections
2. Table management (drop, clear)
3. Data validation
4. Working with multiple databases
"""

import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.postgresql_dataloader import PostgreSQLDataLoader


def example_1_custom_connection():
    """
    Example 1: Connect to a custom database
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Custom Database Connection")
    print("="*80)

    # Option 1: Use default connection (from .env)
    print("\n--- Default Connection ---")
    with PostgreSQLDataLoader() as loader:
        tables = loader.get_all_tables()
        print(f"Connected to default database successfully! Found {len(tables)} tables.")

    # Option 2: Custom connection parameters
    print("\n--- Custom Connection ---")
    try:
        loader = PostgreSQLDataLoader(
            host="localhost",
            port="5432",
            database="test_db",  # Change to your database
            user="postgres",
            password="your_password"
        )
        with loader:
            tables = loader.get_all_tables()
            print(f"Connected to custom database successfully! Found {len(tables)} tables.")
    except Exception as e:
        print(f"Connection failed - check your credentials: {e}")


def example_2_table_management():
    """
    Example 2: Manage tables (create, clear, drop)
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Table Management")
    print("="*80)

    # Create a test table
    df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Test1', 'Test2', 'Test3', 'Test4', 'Test5'],
        'value': [10.5, 20.7, 30.2, 40.9, 50.1]
    })

    with PostgreSQLDataLoader() as loader:
        print("\n--- Creating test table ---")
        loader.create_table_from_dataframe(df, "test_table", primary_key="id")

        # Insert data
        print("\n--- Inserting data ---")
        loader.insert_dataframe(df, "test_table")

        # View data
        print("\n--- Viewing data ---")
        result_df = loader.table_to_dataframe("test_table", limit=5)
        print(result_df)

        # Clear table data
        print("\n--- Clearing table data ---")
        loader.truncate_table("test_table")

        print("\n--- Checking if table is empty ---")
        result_df = loader.table_to_dataframe("test_table", limit=5)
        print(f"Table rows: {len(result_df) if result_df is not None else 0}")

        # Drop table
        print("\n--- Dropping table ---")
        loader.drop_table("test_table")


def example_3_data_validation():
    """
    Example 3: Data type validation and conversion
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Data Validation")
    print("="*80)

    # Create DataFrame with different data types
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'salary': [50000.50, 60000.75, 70000.25],
        'is_active': [True, True, False],
        'join_date': ['2020-01-15', '2019-05-20', '2021-03-10']
    })

    print("\nDataFrame Info:")
    print(df.dtypes)

    with PostgreSQLDataLoader() as loader:
        print("\n--- Creating table with type mapping ---")
        loader.create_table_from_dataframe(df, "validated_employees", primary_key="id")

        print("\n--- Table structure ---")
        table_info = loader.get_table_info("validated_employees")
        if table_info:
            for col in table_info['columns']:
                print(f"  {col['name']}: {col['type']}")

        print("\n--- Inserting validated data ---")
        rows = loader.insert_dataframe(df, "validated_employees")
        print(f"Inserted {rows} rows")

        # Cleanup
        loader.drop_table("validated_employees")


def example_4_batch_operations():
    """
    Example 4: Working with large datasets
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Batch Operations")
    print("="*80)

    # Generate sample data
    import numpy as np

    n_rows = 1000
    df = pd.DataFrame({
        'id': range(1, n_rows + 1),
        'category': np.random.choice(['A', 'B', 'C', 'D'], n_rows),
        'value': np.random.randn(n_rows) * 100,
        'flag': np.random.choice([True, False], n_rows)
    })

    print(f"\nGenerated {len(df)} rows of sample data")

    with PostgreSQLDataLoader() as loader:
        print("\n--- Creating table for batch insert ---")
        loader.create_table_from_dataframe(df, "batch_data", primary_key="id")

        print("\n--- Performing batch insert (batch_size=1000) ---")
        rows = loader.insert_dataframe(df, "batch_data", batch_size=1000)
        print(f"Successfully inserted {rows} rows in batch")

        print("\n--- Viewing sample ---")
        result_df = loader.table_to_dataframe("batch_data", limit=10)
        print(result_df)

        # Cleanup
        loader.drop_table("batch_data")


def example_5_error_handling():
    """
    Example 5: Error handling and recovery
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Error Handling")
    print("="*80)

    with PostgreSQLDataLoader() as loader:
        # Try to insert data into non-existent table
        print("\n--- Attempting to insert into non-existent table ---")
        df = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        result = loader.insert_dataframe(df, "non_existent_table")

        if result is None:
            print("Operation failed as expected (table doesn't exist)")

        # Check if table exists
        print("\n--- Checking if table exists ---")
        exists = loader.table_exists("non_existent_table")
        print(f"Table exists: {exists}")

        # Try to drop non-existent table
        print("\n--- Attempting to drop non-existent table ---")
        result = loader.drop_table("non_existent_table_xyz")

        if not result:
            print("Drop operation completed (table didn't exist anyway)")


def main():
    """
    Run all advanced examples
    """
    print("="*80)
    print("PostgreSQL DataLoader - Advanced Operations")
    print("="*80)

    try:
        # Example 1: Custom connections
        example_1_custom_connection()

        # Example 2: Table management
        example_2_table_management()

        # Example 3: Data validation
        example_3_data_validation()

        # Example 4: Batch operations
        example_4_batch_operations()

        # Example 5: Error handling
        example_5_error_handling()

        print("\n" + "="*80)
        print("All advanced examples completed!")
        print("="*80)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
