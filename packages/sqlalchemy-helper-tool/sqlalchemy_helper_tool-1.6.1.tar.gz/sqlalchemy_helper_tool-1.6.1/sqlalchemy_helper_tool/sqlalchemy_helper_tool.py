from sqlalchemy import create_engine, inspect, text
import pandas as pd
from urllib.parse import quote
import math
from sqlalchemy.pool import NullPool

def _apply_column_case(columns, column_case):
    transformations = {
        'upper': str.upper,
        'lower': str.lower,
        'capitalize': str.capitalize,
        'title': str.title
    }

    func = transformations.get(column_case)

    if func:
        return [func(col) for col in columns]
    return columns

class DbApi:
    """
    Class to handle connections to MySQL or SQL Server databases using SQLAlchemy.

    Example usage:
        db = DbApi(
            server='localhost',
            database='my_db',
            username='user',
            password='pass',
            dialect='mysql',  # or 'mssql'
            driver='ODBC Driver 18 for SQL Server',  # only needed for MSSQL
            port=3306,
            dict_params={"TrustServerCertificate": "yes", "Encrypt": "no"}
        )
    """
    def __init__(self, server, database, username, password, port=None,
                 dict_params=None, dialect='mysql', driver=None):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.dialect = dialect.lower()
        self.driver = driver
        self.dict_params = dict_params or {}

        self.con = self.connect()
        self.allowed_tables = self.load_allowed_tables() 

    def connect(self):
        if self.dialect == 'mysql':
            driver = 'pymysql'
            if self.port:
                url = f"mysql+{driver}://{self.username}:{self.password}@{self.server}:{self.port}/{self.database}"
            else:
                url = f"mysql+{driver}://{self.username}:{self.password}@{self.server}/{self.database}"
            engine = create_engine(
                url, 
                connect_args=self.dict_params,
                poolclass=NullPool  # disables pooling
                )
            return engine

        elif self.dialect == 'mssql':
            driver = 'pyodbc'
            odbc_driver = self.driver or 'ODBC Driver 18 for SQL Server'

            # If the server already has a named instance, do not add the port
            if '\\' in self.server:
                server_str = self.server
            else:
                server_str = f"{self.server},{self.port}" if self.port else self.server

            connect_str = (
                f"DRIVER={odbc_driver};"
                f"SERVER={server_str};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )
            for k, v in self.dict_params.items():
                connect_str += f"{k}={v};"

            # Escape everything except ; and = (let \ escape)
            connect_str_escaped = quote(connect_str, safe=';=')

            # Replace double backslashes with a single backslash
            connect_str_escaped = connect_str_escaped.replace('%5C%5C', '\\')

            connect_uri = f"mssql+pyodbc:///?odbc_connect={connect_str_escaped}"

            engine = create_engine(connect_uri)
            return engine

        else:
            raise ValueError(f"Unsupported dialect '{self.dialect}'")
    
    def load_allowed_tables(self):
        with self.con.connect() as conn:
            inspector = inspect(conn)
            return set(inspector.get_table_names(schema=self.database))
    
    def execute_query(self, query):
        with self.con.connect() as conn: 
            with conn.begin():
                conn.execute(text(query))

    # Checks if table_name exists
    def table_in_db(self, table_name):
        tables_list = self.con.table_names()
        table_in = table_name in tables_list
        return table_in
    
    # Returns column metadata of table_name
    def table_info(self, table_name):
        insp = inspect(self.con)
        columns_table = insp.get_columns(table_name)
        return columns_table

    # Read a SQL table and return a DataFrame
    def read_sql(self, my_query, dict_params=None, column_case='original'):
        if dict_params:
            for k, v in dict_params.items():
                self.con.execute(f"SET @{k} := '{v}';")

        df = pd.read_sql_query(sql=my_query, con=self.con)

        # Apply column name transformation if needed
        df.columns = _apply_column_case(df.columns, column_case)

        return df

    # Returns column names of table_name as list
    def read_columns_table_db(self, table_name, column_case='original'):
        df = self.read_sql(f'SELECT * FROM {table_name} LIMIT 1;', column_case=column_case)
        return df.columns.to_list()
    
    # Add a column_name in table_name
    def add_column(self, table_name, column_name, column_type, existing_column=None):
        if existing_column:  # Only execute if existing_column is not None or empty
            query = f"ALTER TABLE `{table_name}` ADD `{column_name}` {column_type} AFTER `{existing_column}`"
        else:
            query = f"ALTER TABLE `{table_name}` ADD `{column_name}` {column_type}"
        id = self.con.execute(query)

    # Just insert new values (new keys)
    def write_sql_key(self, df, table_name):
        tuple_ = ['%s'] * len(df.columns)
        tuple_ = ','.join(tuple_)

        tuples = [tuple(x) for x in df.values]
        query = f"INSERT IGNORE INTO `{self.database}`.`{table_name}` VALUES({tuple_})"
        id = self.con.execute(query, tuples)

    # Like above, but handles nulls and escapes column names
    def write_sql_key2(self, df, table_name):
        # Clean column names
        columns = [f"`{col.strip().replace('`', '')}`" for col in df.columns]
        values_columns = ', '.join(columns)

        # Placeholders for all columns
        tuple_ = ','.join(['%s'] * len(df.columns))

        tuples = [
            tuple(None if isinstance(v, float) and math.isnan(v) or pd.isna(v) else v
                for v in row)
            for row in df.itertuples(index=False, name=None)
        ]

        # Final query
        query = f"INSERT IGNORE INTO `{self.database}`.`{table_name}` ({values_columns}) VALUES({tuple_})"

        # Execute query
        id = self.con.execute(query, tuples)
    
    # Add new rows (if you add a row with a key that is already in table_name it will give an error)
    def write_sql_df_append(self, df, table_name):
        df.to_sql(table_name, con=self.con, if_exists='append', index=False)

    # Deletes all rows in a table or a LIMIT
    def delete_table(self, table_name, limit=None):
        if self.table_in_db(table_name):
            if limit:  # Only execute if limit is not None or empty
                query = f"DELETE FROM `{table_name}` LIMIT {limit}"
            else:
                query = f"DELETE FROM `{table_name}`"
            id = self.con.execute(query)

    # Removes a column from table_name
    def delete_column(self, table_name, column_name):
        if ' ' in column_name:
            column_name = "`" + column_name + "`"
        if self.table_in_db(table_name):
            query = f"ALTER TABLE `{table_name}` DROP `{column_name}`"
            id = self.con.execute(query)

    # Deletes all rows and inserts new ones, preserving schema
    def write_sql_df_replace(self, df, table_name):
        # Delete table values                                 # If I use
        self.delete_table(table_name)                         # df.to_sql(table_name, con=con, if_exists='replace', index=False)
                                                             # instead of this code the table table_name
                                                             # is deleted first and I lose the characteristics 
                                                             # of the table I already created initially
                                                             # (keys, column's types....)
        df.to_sql(table_name, con=self.con, if_exists='append', index=False)

    # Replaces specific values via ON DUPLICATE KEY UPDATE
    def replace_sql_values(self, df, table_name, column_replace, columns_key):
        df = df[[columns_key] + [column_replace]]
    
        values_columns = str(tuple(df.columns))              # See if I can see all this prittier
        values_columns = values_columns.replace('(', '')     #
        values_columns = values_columns.replace(')', '')     #
        values_columns = values_columns.replace("'", '')     #
        tuples = ','.join([str(tuple(x)) for x in df.values])

        id = self.con.execute(f"INSERT INTO `{table_name}` ({values_columns}) VALUES {tuples} ON DUPLICATE KEY UPDATE `{column_replace}`=VALUES(`{column_replace}`);")

    # Safe UPDATE method with dynamic conditions
    def update_single_value(self, table_name, column_name, new_value, conditions: dict):
        # Convert the new value to SQL-safe string
        if isinstance(new_value, str):
            new_value_str = f"'{new_value}'"
        elif new_value is None:
            new_value_str = "NULL"
        else:
            new_value_str = str(new_value)

        # Build the WHERE clause from the conditions dictionary
        condition_clauses = []
        for key, value in conditions.items():
            if value is None:
                clause = f"{key} IS NULL"
            elif isinstance(value, str):
                clause = f"{key} = '{value}'"
            else:
                clause = f"{key} = {value}"
            condition_clauses.append(clause)

        where_clause = " AND ".join(condition_clauses)

        # Construct the final SQL UPDATE query
        query = f"UPDATE {table_name} SET {column_name} = {new_value_str} WHERE {where_clause}"

        print(f"Executing query: {query}")  # Debugging output
        # Execute the query using the existing method (no params or commit arguments)
        self.execute_query(query)