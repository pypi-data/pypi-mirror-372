from datetime import timedelta

class TaskModel:
    def __init__(self, default_task_params: dict):
        """
        Represents a configurable Apache Airflow Task model.

        Attributes:
            
            task_id (str): Unique identifier for the task. Required.
            
            dag (Optional[str]): DAG object or DAG id to which this task belongs. Defaults to None.
            
            retries (int): Number of retries if task fails. Defaults to 0.
            
            retry_delay (timedelta): Time delay between retries. Defaults to 5 minutes.
            
            retry_exponential_backoff (bool): Whether retries use exponential backoff. Defaults to False.
            
            max_retry_delay (Optional[timedelta]): Maximum retry delay. Defaults to None.
            
            start_date (Optional[datetime]): Start date of the task. Defaults to None.
            
            end_date (Optional[datetime]): End date of the task. Defaults to None.
            
            depends_on_past (bool): Whether task depends on previous runs. Defaults to False.
            
            wait_for_downstream (bool): Wait for downstream tasks before marking success. Defaults to False.
            
            priority_weight (int): Priority weight of the task. Defaults to 1.
            
            weight_rule (str): Rule for weighing tasks ('upstream'/'downstream'). Defaults to 'upstream'.
            
            pool (Optional[str]): Pool name to control concurrency. Defaults to None.
            
            queue (Optional[str]): Queue name for execution. Defaults to None.
            
            executor_config (dict): Executor configuration. Defaults to {}.
            
            sla (Optional[timedelta]): SLA for the task. Defaults to None.
            
            on_success_callback (Optional[Callable]): Function called on success. Defaults to None.
            
            on_failure_callback (Optional[Callable]): Function called on failure. Defaults to None.
            
            trigger_rule (str): Trigger rule for task execution. Defaults to 'all_success'.
            
            doc_md (str): Documentation in Markdown format. Defaults to ''.
            
            params (dict): Custom parameters available in task templates. Defaults to {}.
        """
        
        self.task_id = default_task_params.get('task_id', 'default_task')
        
        self.dag = default_task_params.get('dag', None)
        
        self.retries = default_task_params.get('retries', 0)
        
        self.retry_delay = default_task_params.get('retry_delay', timedelta(minutes=5))
        
        self.retry_exponential_backoff = default_task_params.get('retry_exponential_backoff', False)
        
        self.max_retry_delay = default_task_params.get('max_retry_delay', None)
        
        self.start_date = default_task_params.get('start_date', None)
        
        self.end_date = default_task_params.get('end_date', None)
        
        self.depends_on_past = default_task_params.get('depends_on_past', False)
        
        self.wait_for_downstream = default_task_params.get('wait_for_downstream', False)
        
        self.priority_weight = default_task_params.get('priority_weight', 1)
        
        self.weight_rule = default_task_params.get('weight_rule', 'upstream')
        
        self.pool = default_task_params.get('pool', None)
        
        self.queue = default_task_params.get('queue', None)
        
        self.executor_config = default_task_params.get('executor_config', {})
        
        self.sla = default_task_params.get('sla', None)
        
        self.on_success_callback = default_task_params.get('on_success_callback', None)
        
        self.on_failure_callback = default_task_params.get('on_failure_callback', None)
        
        self.trigger_rule = default_task_params.get('trigger_rule', 'all_success')
        
        self.doc_md = default_task_params.get('doc_md', "")
        
        self.params = default_task_params.get('params', {})
