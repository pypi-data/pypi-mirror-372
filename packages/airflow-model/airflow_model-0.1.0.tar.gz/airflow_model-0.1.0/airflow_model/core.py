import logging
from airflow import DAG
from datetime import datetime
from airflow.operators.bash import BashOperator  # type: ignore
from airflow.operators.python import PythonOperator  # type: ignore
from airflow.providers.postgres.hooks.postgres import PostgresHook
from typing import List, Dict, Any  # ✅ Tipagem mais clara


class AirflowModel:
    def __init__(self, default_dags_params: dict):
        # configurações padrão da DAG
        data_atual = datetime.now()

        self.name_dag = default_dags_params.get('name_dag', 'default_dag')
        self.start_date = default_dags_params.get(
            'start_date',
            datetime(data_atual.year, data_atual.month, data_atual.day)
        )
        self.schedule = default_dags_params.get('schedule', '30 1 * * *')
        self.catchup = default_dags_params.get('catchup', False)
        self.description = default_dags_params.get(
            'description', f'DAG name {self.name_dag}'
        )
        self.tags = default_dags_params.get('tags', ['default', 'root'])

    def default_funtion(self, **kwargs) -> None: 
        print('Função padrão executada (sem ação específica)')

    def configuration_dag_root(self):
        try:
            with DAG(
                dag_id=self.name_dag,
                description=self.description,
                schedule_interval=self.schedule,
                start_date=self.start_date,
                catchup=self.catchup,
                tags=self.tags
            ) as dag:
                return dag

        except Exception as erro:
            logging.error("Erro ao configurar a DAG: %s", erro)
            raise

    def configuration_task(self, default_task_params: List[Dict[str, Any]]):
        try:
            tasks = []
            for task in default_task_params:
                id_verification = task.get('task_type', 'empty')

                if id_verification.lower() == 'python':
                    task_python = PythonOperator(
                        task_id=task.get('task_id', 'task_python_default'),
                        python_callable=task.get(
                            'python_callable',
                            self.default_funtion
                        ),
                        op_args=task.get('op_args', []),
                        op_kwargs=task.get('op_kwargs', {}),
                    )
                    tasks.append({"type_task": "Python", "task": task_python})

                elif id_verification.lower() == 'bash':
                    task_bash = BashOperator(
                        task_id=task.get('task_id', 'task_bash_default'),
                        bash_command=task.get(
                            'bash_command',
                            'echo "Comando não executado pois não se tem conhecimento sobre o mesmo"'
                        )
                    )
                    tasks.append({"type_task": "Bash", "task": task_bash})

            return tasks

        except Exception as erro:
            logging.error("Erro ao configurar a TASK: %s", erro)

    def connection_database(self, default_params_connection: dict):
        conn = None
        cursor = None
        try:
            type_connection = default_params_connection.get('type', 'default')
            if type_connection.lower() == 'postgres':
                hook = PostgresHook(
                    postgres_conn_id=default_params_connection.get(
                        'id_connection_airflow', 'postgres'
                    )
                )
                conn = hook.get_conn()
                cursor = conn.cursor()

                query = default_params_connection.get("query", None)
                if query:
                    cursor.execute(query)
                else:
                    with open(
                        default_params_connection.get(
                            'path_arquive_sql', '.sql'
                        ),
                        'r'
                    ) as f:
                        sql_command = f.read()
                    cursor.execute(sql_command)

                results = cursor.fetchall()
                return results

        except Exception as erro:
            logging.error(
                "Erro ao configurar as conexões para o banco de dados: %s",
                erro
            )
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
