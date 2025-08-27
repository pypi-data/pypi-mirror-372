import logging
from models.PostgresModel import PostgresModel
from airflow.providers.postgres.hooks.postgres import PostgresHook

class PostgresConstructor(PostgresModel):
    def __init__(self, default_postgres_params: dict):
        """
        PostgresConstructor initializes a Postgres connection model with full parameters.

        Args:
            default_postgres_params (dict): Dictionary with default parameters for Postgres connection:
                - id_connection: Airflow connection ID.
                - type_connection: Type of connection (e.g., 'postgres').
                - string_query: SQL query string to execute.
                - path_file_query: Path to SQL file to execute.
                - file_query_permission: File permission mode, default 'r'.
        """
        super().__init__(default_postgres_params)

    def execute_query(self, params_connection: dict = None):
        """
        Executes a query on the Postgres database using the connection parameters.

        Args:
            params_connection (dict, optional): Optional dictionary with override parameters:
                - id_connection_airflow: Airflow connection ID.
                - type: Connection type, e.g., 'postgres'.
                - query: SQL string to execute.
                - path_arquive_sql: Path to SQL file to execute.

        Returns:
            List[Tuple]: Results from the query execution.
        """
        conn = None
        cursor = None
        try:
            if params_connection is None:
                params_connection = {}

            connection_type = params_connection.get('type', self.connection_type).lower()
            if connection_type == 'postgres':
                hook = PostgresHook(
                    postgres_conn_id=params_connection.get('id_connection_airflow', self.connection_id)
                )
                conn = hook.get_conn()
                cursor = conn.cursor()

                query = params_connection.get('query', self.string_query)
                if query:
                    cursor.execute(query)
                else:
                    path_file = params_connection.get('path_arquive_sql', self.query_file_path)
                    file_mode = params_connection.get('permission_file_query', self.file_query_permission)
                    with open(path_file, file_mode) as f:
                        sql_command = f.read()
                    cursor.execute(sql_command)

                results = cursor.fetchall()
                return results

            else:
                logging.warning("Unsupported connection type: %s", connection_type)
                return []

        except Exception as erro:
            logging.error("Error executing Postgres query: %s", erro)
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
