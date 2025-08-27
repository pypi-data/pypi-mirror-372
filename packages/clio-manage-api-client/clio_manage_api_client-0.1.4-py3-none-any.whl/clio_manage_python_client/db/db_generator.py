from typing import Optional, Literal
import sqlite3
import datetime
from dataclasses import fields, is_dataclass
    
from ..models.components import *  # Import all dataclasses from components.py

def get_sql_type(py_type):
    """
    Maps Python types to SQLite types.
    """
    if py_type in (int, Optional[int]):
        return "INTEGER"
    elif py_type in (float, Optional[float]):
        return "REAL"
    elif py_type in (str, Optional[str], Literal):
        return "TEXT"
    elif py_type in (bool, Optional[bool]):
        return "INTEGER"  
    elif py_type in (datetime.datetime, Optional[datetime.datetime]):
        return "TEXT"
    else:
        return "TEXT"

def create_table_sql(class_name, dataclass_obj):
    """
    Generates the SQL statement to create a table for the given dataclass.
    """
    reserved_keywords = {"default", "order", "group", "index", "table", "values", "key", "primary"}
    column_definitions = []
    for field in fields(dataclass_obj):
        column_name = field.name
        if column_name.lower() in reserved_keywords:
            column_name = f'"{field.name}"'  # Escape reserved keywords
        column_type = get_sql_type(field.type)
        
        if column_name == "id":
            column_definitions.append(f"{column_name} {column_type} PRIMARY KEY UNIQUE")
        else:
            column_definitions.append(f"{column_name} {column_type}")

    if not column_definitions:
        return None  # Skip dataclass with no fields
    
    column_definitions.append(f"endpoint_relationships TEXT")
    
    columns_str = ", ".join(column_definitions)
    return f"CREATE TABLE IF NOT EXISTS {class_name} ({columns_str});"

def generate_database(db_name="database.db"):
    """
    Creates an SQLite database and generates tables from dataclasses.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Retrieve all dataclasses defined in models.schemas
    for class_name, class_obj in globals().items():
        if isinstance(class_obj, type) and is_dataclass(class_obj):
            create_sql = create_table_sql(class_name, class_obj)
            if create_sql:  # Only execute if SQL string is valid
                cursor.execute(create_sql)
                # print(f"Table created: {class_name}")
            else:
                print(f"Skipped {class_name}, no fields to create table.")
    
    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created successfully.")

if __name__ == "__main__":
    generate_database()