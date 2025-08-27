class PostgresModel:
    def __init__(self, default_postgres_params: dict):
        
        self.connection_id = default_postgres_params.get('id_connection', '')
        
        connection_base_type = default_postgres_params.get('type_connection', '')
        self.connection_type = connection_base_type.lower()

        self.string_query = default_postgres_params.get('string_query', '')

        self.query_file_path = default_postgres_params.get('path_file_query', '')

        self.file_query_permission = default_postgres_params.get('permission_file_query', 'r')
        