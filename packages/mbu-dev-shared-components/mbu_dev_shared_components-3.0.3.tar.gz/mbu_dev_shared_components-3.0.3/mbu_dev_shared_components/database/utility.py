"""This module handles general database connection and calls"""

import os
import json
from typing import Dict, Union, Tuple, Any
from dateutil import parser
import pyodbc


class Utility:
    """Base class handling general utilities"""
    def connect_to_db(self, autocommit=True, db_env="PROD") -> pyodbc.Connection:
        """Establish connection to sql database

        Returns:
            rpa_conn (pyodbc.Connection): The connection object to the SQL database.
        """
        connection_env = self.fetch_env(db_env)
        rpa_conn_string = os.getenv(connection_env)
        rpa_conn = pyodbc.connect(rpa_conn_string, autocommit=autocommit)
        return rpa_conn

    def execute_query(self, query: str, params: list = None) -> pyodbc.Cursor:
        """Execute SQL query with pyodbc"""
        params = [] if not params else params
        is_select = query.strip().upper().startswith('SELECT')
        try:
            res = self.cursor.execute(query, params)
            if is_select:
                res = self.cursor.fetchall()
                if len(res) == 0:
                    print("No results from query")
                    return None
                return res
            else:
                return None
        except pyodbc.Error as e:
            print(e)
            print(query)
            raise e

    def fetch_env(self, db_env):
        """Get env variable based on context, PROD or TEST"""
        if db_env.upper() == "PROD":
            connection_env = "DbConnectionString"
            return connection_env
        if db_env.upper() == "TEST":
            connection_env = "DbConnectionStringTest"
            return connection_env

        raise ValueError(f"arg db_env is {db_env.upper()} but should be 'PROD' or 'TEST'")

    def execute_stored_procedure(self, stored_procedure: str, params: Dict[str, Tuple[type, Any]] | None = None) -> Dict[str, Union[bool, str, Any]]:
        """
        Executes a stored procedure with the given parameters.

        Args:
            connection_string (str): The connection string to connect to the database.
            stored_procedure (str): The name of the stored procedure to execute.
            params (Dict[str, Tuple[type, Any]], optional): A dictionary of parameters to pass to the stored procedure.
                                    Each value should be a tuple of (type, actual_value).

        Returns:
            Dict[str, Union[bool, str, Any]]: A dictionary containing the success status, an error message (if any),
                                            number of affected rows, and additional data.
        """
        result = {
            "success": False,
            "error_message": None,
        }

        type_mapping = {
            "str": str,
            "int": int,
            "float": float,
            "datetime": parser.isoparse,
            "json": lambda x: json.dumps(x, ensure_ascii=False)
        }

        try:
            if params:
                param_placeholders = ', '.join([f"@{key} = ?" for key in params.keys()])
                param_values = []

                for key, value in params.items():
                    if isinstance(value, tuple) and len(value) == 2:
                        value_type, actual_value = value
                        if value_type in type_mapping:
                            param_values.append(type_mapping[value_type](actual_value))
                        else:
                            param_values.append(actual_value)
                    else:
                        raise ValueError("Each parameter value must be a tuple of (type, actual_value).")

                sql = f"EXEC {stored_procedure} {param_placeholders}"
                rows_updated = self.cursor.execute(sql, tuple(param_values))
            else:
                sql = f"EXEC {stored_procedure}"
                rows_updated = self.cursor.execute(sql)
            result["success"] = True
            result["rows_updated"] = rows_updated.rowcount
        except pyodbc.Error as e:
            result["error_message"] = f"Database error: {str(e)}"
        except ValueError as e:
            result["error_message"] = f"Value error: {str(e)}"
        except Exception as e:
            result["error_message"] = f"An unexpected error occurred: {str(e)}"

        return result
