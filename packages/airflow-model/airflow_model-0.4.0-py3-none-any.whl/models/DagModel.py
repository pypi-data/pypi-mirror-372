from datetime import datetime

class DagModel:
    def __init__(self, default_dags_params: dict):
        """
        Represents a configurable Apache Airflow DAG model with full parameters.

        Attributes:
            
            name_dag (str): Name of the DAG. Defaults to 'default_dag'.
            
            start_date (datetime): Start date of the DAG. Defaults to today.
            
            end_date (Optional[datetime]): End date of the DAG. Defaults to None.
            
            schedule (str): Cron expression or preset for the DAG schedule. Defaults to '30 1 * * *'.
            
            catchup (bool): Whether the DAG should perform backfill. Defaults to False.
            
            default_args (dict): Default args passed to tasks. Defaults to {}.
            
            max_active_runs (int): Maximum number of active DAG runs. Defaults to 16.
            
            concurrency (int): Maximum number of tasks to run concurrently. Defaults to 16.
            
            dagrun_timeout (Optional[timedelta]): Max time for a DAG run. Defaults to None.
            
            on_success_callback (Optional[Callable]): Function to call on DAG success. Defaults to None.
            
            on_failure_callback (Optional[Callable]): Function to call on DAG failure. Defaults to None.
            
            doc_md (str): Documentation in Markdown. Defaults to empty string.
            
            is_paused_upon_creation (bool): Whether DAG starts paused. Defaults to True.
            
            tags (List[str]): Tags associated with the DAG. Defaults to ['default', 'root'].
            
            params (dict): Custom params accessible by tasks. Defaults to {}.
            
            template_searchpath (List[str]): Paths to search for templates. Defaults to None.
            
            timezone (str): Timezone for DAG. Defaults to 'UTC'.
            
            description (str): Description of the DAG. Defaults to 'DAG name <name_dag>'.
        """
        now = datetime.now()

        self.name_dag = default_dags_params.get('name_dag', 'default_dag')
        
        self.start_date = default_dags_params.get(
            'start_date',
            datetime(now.year, now.month, now.day)
        )
        
        self.end_date = default_dags_params.get('end_date', None)
        
        self.schedule = default_dags_params.get('schedule', '30 1 * * *')
        
        self.catchup = default_dags_params.get('catchup', False)
        
        self.default_args = default_dags_params.get('default_args', {})
        
        self.max_active_runs = default_dags_params.get('max_active_runs', 16)
        
        self.concurrency = default_dags_params.get('concurrency', 16)
        
        self.dagrun_timeout = default_dags_params.get('dagrun_timeout', None)
        
        self.on_success_callback = default_dags_params.get('on_success_callback', None)
        
        self.on_failure_callback = default_dags_params.get('on_failure_callback', None)
        
        self.doc_md = default_dags_params.get('doc_md', "")
        
        self.is_paused_upon_creation = default_dags_params.get('is_paused_upon_creation', True)
        
        self.tags = default_dags_params.get('tags', ['default', 'root'])
        
        self.params = default_dags_params.get('params', {})
        
        self.template_searchpath = default_dags_params.get('template_searchpath', None)
        
        self.timezone = default_dags_params.get('timezone', 'UTC')
        
        self.description = default_dags_params.get(
            'description', f'DAG name {self.name_dag}'
        )
