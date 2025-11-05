#!/usr/bin/env python3
"""Script to check database tables."""

from sqlalchemy import inspect
from app.database import engine

def list_tables():
    """List all tables in the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("Database Tables:")
    print("-" * 50)

    if not tables:
        print("No tables found in the database.")
        return

    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")

        # Get column information
        columns = inspector.get_columns(table)
        print(f"   Columns ({len(columns)}):")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            print(f"     - {col['name']}: {col['type']} {nullable}{default}")

        # Get indexes
        indexes = inspector.get_indexes(table)
        if indexes:
            print(f"   Indexes ({len(indexes)}):")
            for idx in indexes:
                unique = "UNIQUE" if idx['unique'] else ""
                cols = ", ".join(idx['column_names'])
                print(f"     - {idx['name']} {unique}: ({cols})")

        print()

    print(f"Total tables: {len(tables)}")

if __name__ == "__main__":
    try:
        list_tables()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. The .env file is configured correctly")
        print("3. The database exists and credentials are correct")


