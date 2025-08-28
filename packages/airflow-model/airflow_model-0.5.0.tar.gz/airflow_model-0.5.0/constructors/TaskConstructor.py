import logging
from typing import List, Dict, Any
from airflow.operators.python import PythonOperator #type: ignore
from airflow.operators.bash import BashOperator     #type: ignore
from models.TaskModel import TaskModel

class TaskConstructor(TaskModel):
    def __init__(self, default_task_params: dict, default_function=None):
        """
        TaskConstructor initializes a task with default parameters from TaskModel.

        Args:
            default_task_params (dict): Dictionary with default parameters for the task.
            default_function (Callable, optional): Default function for PythonOperator if none provided.
        """
        super().__init__(default_task_params)
        self.default_function = default_function

    def configuration_task(self, tasks_params: List[Dict[str, Any]]):
        """
        Configures Airflow tasks (PythonOperator or BashOperator) using TaskModel parameters.

        Args:
            tasks_params (List[Dict[str, Any]]): List of dictionaries for each task containing:
                - task_type: 'python' or 'bash'
                - task_id: unique identifier
                - python_callable: function for PythonOperator (optional)
                - op_args: positional arguments for PythonOperator (optional)
                - op_kwargs: keyword arguments for PythonOperator (optional)
                - bash_command: command string for BashOperator (optional)

        Returns:
            List[Dict[str, Any]]: List of dicts containing task type and task object.
        """
        try:
            tasks = []

            for task_param in tasks_params:
                task_type = task_param.get('task_type', 'empty').lower()

                if task_type == 'python':
                    python_task = PythonOperator(
                        
                        task_id=task_param.get('task_id', self.task_id),
                        
                        python_callable=task_param.get('python_callable', self.default_function),
                        
                        op_args=task_param.get('op_args', []),
                        
                        op_kwargs=task_param.get('op_kwargs', {}),
                        
                        dag=task_param.get('dag', self.dag),
                        
                        retries=task_param.get('retries', self.retries),
                        
                        retry_delay=task_param.get('retry_delay', self.retry_delay),
                        
                        retry_exponential_backoff=task_param.get('retry_exponential_backoff', self.retry_exponential_backoff),
                        
                        max_retry_delay=task_param.get('max_retry_delay', self.max_retry_delay),
                        
                        start_date=task_param.get('start_date', self.start_date),
                        
                        end_date=task_param.get('end_date', self.end_date),
                        
                        depends_on_past=task_param.get('depends_on_past', self.depends_on_past),
                        
                        wait_for_downstream=task_param.get('wait_for_downstream', self.wait_for_downstream),
                        
                        priority_weight=task_param.get('priority_weight', self.priority_weight),
                        
                        weight_rule=task_param.get('weight_rule', self.weight_rule),
                        
                        pool=task_param.get('pool', self.pool),
                        
                        queue=task_param.get('queue', self.queue),
                        
                        executor_config=task_param.get('executor_config', self.executor_config),
                        
                        sla=task_param.get('sla', self.sla),
                        
                        on_success_callback=task_param.get('on_success_callback', self.on_success_callback),
                        
                        on_failure_callback=task_param.get('on_failure_callback', self.on_failure_callback),
                        
                        trigger_rule=task_param.get('trigger_rule', self.trigger_rule),
                        
                        doc_md=task_param.get('doc_md', self.doc_md),
                        
                        params=task_param.get('params', self.params)
                    )
                    tasks.append({"type_task": "Python", "task": python_task})

                elif task_type == 'bash':
                    bash_task = BashOperator(
                        
                        task_id=task_param.get('task_id', self.task_id),
                        
                        bash_command=task_param.get('bash_command', 'echo "No bash command provided"'),
                        
                        dag=task_param.get('dag', self.dag),
                        
                        retries=task_param.get('retries', self.retries),
                        
                        retry_delay=task_param.get('retry_delay', self.retry_delay),
                        
                        retry_exponential_backoff=task_param.get('retry_exponential_backoff', self.retry_exponential_backoff),
                        
                        max_retry_delay=task_param.get('max_retry_delay', self.max_retry_delay),
                        
                        start_date=task_param.get('start_date', self.start_date),
                        
                        end_date=task_param.get('end_date', self.end_date),
                        
                        depends_on_past=task_param.get('depends_on_past', self.depends_on_past),
                        
                        wait_for_downstream=task_param.get('wait_for_downstream', self.wait_for_downstream),
                        
                        priority_weight=task_param.get('priority_weight', self.priority_weight),
                        
                        weight_rule=task_param.get('weight_rule', self.weight_rule),
                        
                        pool=task_param.get('pool', self.pool),
                        
                        queue=task_param.get('queue', self.queue),
                        
                        executor_config=task_param.get('executor_config', self.executor_config),
                        
                        sla=task_param.get('sla', self.sla),
                        
                        on_success_callback=task_param.get('on_success_callback', self.on_success_callback),
                        
                        on_failure_callback=task_param.get('on_failure_callback', self.on_failure_callback),
                        
                        trigger_rule=task_param.get('trigger_rule', self.trigger_rule),
                        
                        doc_md=task_param.get('doc_md', self.doc_md),
                        
                        params=task_param.get('params', self.params)
                    )
                    tasks.append({"type_task": "Bash", "task": bash_task})

            return tasks

        except Exception as erro:
            logging.error("Error configuring task: %s", erro)
            raise
