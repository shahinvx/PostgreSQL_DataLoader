"""
Basic Usage Examples for PostgreSQL DataLoader

This script demonstrates the fundamental operations:
1. Loading CSV data
2. Creating tables from DataFrames
3. Inserting data into tables
4. Querying and exploring data
"""

import pandas as pd
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.postgresql_dataloader import (
    create_table_from_dataframe,
    insert_dataframe_to_table,
    print_all_table_names,
    print_table_columns,
    select_top_n_rows,
    get_table_column_names
)


def clean_numeric_column(series):
    """Helper function to clean numeric columns with commas"""
    if series.dtype == 'object':
        return series.str.replace(',', '').replace('', None)
    return series


def example_1_load_customer_demographics():
    """
    Example 1: Load customer demographics from CSV
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Loading Customer Demographics")
    print("="*80)

    # Read CSV file
    csv_path = "../data/sample_customer_demographics.csv"
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    print(f"\nLoaded {len(df)} rows from CSV")
    print(f"Columns: {df.columns.tolist()}")

    # Clean numeric columns
    numeric_cols = [
        'Monthly Total Deposit Limit',
        'Monthly Total Withdrawal Limit',
        'Total Number of Active CASA Accounts',
        'Total Number of Active TD Accounts',
        'Total Number of Active Loan Accounts'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric_column(df[col])

    # Rename long columns (PostgreSQL has 63-char limit)
    column_mapping = {}
    for col in df.columns:
        if len(col) > 63:
            column_mapping[col] = col[:63]

    if column_mapping:
        df.rename(columns=column_mapping, inplace=True)

    # Create table
    print("\nCreating table 'demo_customers'...")
    success = create_table_from_dataframe(df, "demo_customers")

    if success:
        # Insert data
        print("\nInserting data...")
        rows = insert_dataframe_to_table(df, "demo_customers")
        print(f"\nSuccessfully inserted {rows} rows!")

        # Verify
        print("\nVerifying data...")
        select_top_n_rows("demo_customers", limit=3)


def example_2_load_transactions():
    """
    Example 2: Load transaction data from CSV
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Loading Transaction Data")
    print("="*80)

    # Read CSV
    csv_path = "../data/sample_customer_transactions.csv"
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    print(f"\nLoaded {len(df)} rows from CSV")

    # Clean numeric columns
    for col in ['WITHDRAW', 'DEPOSIT', 'BALANCE']:
        if col in df.columns:
            df[col] = clean_numeric_column(df[col])

    # Create table
    print("\nCreating table 'demo_transactions'...")
    success = create_table_from_dataframe(df, "demo_transactions")

    if success:
        # Insert data
        print("\nInserting data...")
        rows = insert_dataframe_to_table(df, "demo_transactions")
        print(f"\nSuccessfully inserted {rows} rows!")

        # Verify
        print("\nVerifying data...")
        select_top_n_rows("demo_transactions", limit=5)


def example_3_explore_database():
    """
    Example 3: Explore the database
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Exploring Database")
    print("="*80)

    # List all tables
    print("\n--- All Tables ---")
    print_all_table_names()

    # Inspect table structure
    print("\n--- Customer Table Structure ---")
    print_table_columns("demo_customers")

    # Get column names
    print("\n--- Transaction Columns ---")
    columns = get_table_column_names("demo_transactions")
    print(f"Columns: {columns}")


def main():
    """
    Run all examples
    """
    print("="*80)
    print("PostgreSQL DataLoader - Basic Usage Examples")
    print("="*80)

    try:
        # Example 1: Load demographics
        example_1_load_customer_demographics()

        # Example 2: Load transactions
        example_2_load_transactions()

        # Example 3: Explore database
        example_3_explore_database()

        print("\n" + "="*80)
        print("All examples completed successfully!")
        print("="*80)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
