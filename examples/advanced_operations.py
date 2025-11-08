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

from src.postgresql_dataloader import (
    get_connection,
    create_table_from_dataframe,
    insert_dataframe_to_table,
    drop_table,
    clear_table_data,
    print_table_columns,
    select_top_n_rows
)


def example_1_custom_connection():
    """
    Example 1: Connect to a custom database
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Custom Database Connection")
    print("="*80)

    # Option 1: Use default connection
    print("\n--- Default Connection ---")
    conn = get_connection()
    if conn:
        print("Connected to default database successfully!")
        conn.close()

    # Option 2: Custom connection parameters
    print("\n--- Custom Connection ---")
    conn = get_connection(
        host="localhost",
        port="5432",
        database="test_db",  # Change to your database
        user="postgres",
        password="your_password"
    )
    if conn:
        print("Connected to custom database successfully!")
        conn.close()
    else:
        print("Connection failed - check your credentials")


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

    print("\n--- Creating test table ---")
    create_table_from_dataframe(df, "test_table", primary_key="id")

    # Insert data
    print("\n--- Inserting data ---")
    insert_dataframe_to_table(df, "test_table")

    # View data
    print("\n--- Viewing data ---")
    select_top_n_rows("test_table", limit=5)

    # Clear table data
    print("\n--- Clearing table data ---")
    clear_table_data("test_table")

    print("\n--- Checking if table is empty ---")
    select_top_n_rows("test_table", limit=5)

    # Drop table
    print("\n--- Dropping table ---")
    drop_table("test_table")


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

    print("\n--- Creating table with type mapping ---")
    create_table_from_dataframe(df, "validated_employees", primary_key="id")

    print("\n--- Table structure ---")
    print_table_columns("validated_employees")

    print("\n--- Inserting validated data ---")
    rows = insert_dataframe_to_table(df, "validated_employees")
    print(f"Inserted {rows} rows")

    # Cleanup
    drop_table("validated_employees")


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

    print("\n--- Creating table for batch insert ---")
    create_table_from_dataframe(df, "batch_data", primary_key="id")

    print("\n--- Performing batch insert (page_size=1000) ---")
    rows = insert_dataframe_to_table(df, "batch_data")
    print(f"Successfully inserted {rows} rows in batch")

    print("\n--- Viewing sample ---")
    select_top_n_rows("batch_data", limit=10)

    # Cleanup
    drop_table("batch_data")


def example_5_error_handling():
    """
    Example 5: Error handling and recovery
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Error Handling")
    print("="*80)

    # Try to insert data into non-existent table
    print("\n--- Attempting to insert into non-existent table ---")
    df = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
    result = insert_dataframe_to_table(df, "non_existent_table")

    if result is None:
        print("Operation failed as expected (table doesn't exist)")

    # Try to drop non-existent table
    print("\n--- Attempting to drop non-existent table ---")
    result = drop_table("non_existent_table_xyz")

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
