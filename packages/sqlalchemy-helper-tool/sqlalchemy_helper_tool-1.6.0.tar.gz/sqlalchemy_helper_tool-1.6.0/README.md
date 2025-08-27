
# sqlalchemy_helper_tool

A lightweight Python utility class for simplified interaction with MySQL databases using SQLAlchemy and Pandas. It provides convenient methods to read, write, and modify data or schema with minimal boilerplate.

## Features

- Easy connection setup to a MySQL database using SQLAlchemy
- Execute raw SQL queries
- Inspect tables and columns
- Read SQL results into Pandas DataFrames
- Append, replace, or ignore duplicate rows when writing
- Dynamically add or remove columns
- Parameterized queries
- Auto-handle nulls in inserts
- Safe "replace" of data while preserving table schema

## Installation

Install via pip (requires `sqlalchemy`, `pymysql`, and `pandas`):

```bash
pip install sqlalchemy_helper_tool
```

Clone this repository if needed:

```bash
git clone https://github.com/anakings/sqlalchemy_helper_tool.git
```

## Usage

```python
from sqlalchemy_helper_tool import DbApi

db = DbApi(
    server='localhost',
    database='my_db',
    username='user',
    password='pass'
)

# Run a SQL query
result = db.execute_query("SELECT COUNT(*) FROM users")

# Read a SQL query as DataFrame
df = db.read_sql("SELECT * FROM users LIMIT 10")

# Check if a table exists
exists = db.table_in_db("users")

# Add a new column after an existing one
db.add_column("users", "new_col", "existing_col")

# Write DataFrame ignoring duplicates
db.write_sql_key(df, "users")

# Append rows to an existing table
db.write_sql_df_append(df, "users")

# Replace all data in a table but keep schema
db.write_sql_df_replace(df, "users")

# Replace values in a specific column using a key
db.replace_sql_values(df, "users", column_replace="status", columns_key="id")

# Delete all rows in a table
db.delete_table("users")

# Drop a column
db.delete_column("users", "new_col")
```

## Class: `DbApi`

### Initialization

```python
DbApi(server, database, username, password, dict_params=None)
```

### Key Methods

| Method | Description |
|--------|-------------|
| `execute_query(query)` | Executes a raw SQL query |
| `read_sql(query, dict_params=None)` | Executes a SQL query and returns a DataFrame |
| `table_in_db(table_name)` | Checks if table exists |
| `table_info(table_name)` | Returns column metadata |
| `read_columns_table_db(table_name)` | Returns column names as list |
| `add_column(table_name, column_name, after_column)` | Adds a column |
| `delete_column(table_name, column_name)` | Removes a column |
| `delete_table(table_name)` | Deletes all rows in a table |
| `write_sql_key(df, table_name)` | Inserts ignoring duplicates |
| `write_sql_key2(df, table_name)` | Like above, but handles nulls and escapes column names |
| `write_sql_df_append(df, table_name)` | Appends to table |
| `write_sql_df_replace(df, table_name)` | Deletes all rows and inserts new ones, preserving schema |
| `replace_sql_values(df, table_name, column_replace, columns_key)` | Replaces specific values via ON DUPLICATE KEY UPDATE |

## Requirements

- Python 3.6+
- SQLAlchemy
- pymysql
- pandas

## License

MIT License

## Author

[Anabel Reyes](https://github.com/anakings)
