import logging
from airflow import DAG
from models.DagModel import DagModel

class DagConstructor(DagModel):
    def constructorDag(self):
        """
        Constructs an Airflow DAG using all parameters from DagModel.

        Returns:
            DAG: Configured Airflow DAG object
        """
        try:
            dag = DAG(
                
                dag_id=self.name_dag,
                
                description=self.description,
                
                start_date=self.start_date,
                
                end_date=self.end_date,
                
                schedule_interval=self.schedule,
                
                catchup=self.catchup,
                
                default_args=self.default_args,
                
                max_active_runs=self.max_active_runs,
                
                concurrency=self.concurrency,
                
                dagrun_timeout=self.dagrun_timeout,
                
                on_success_callback=self.on_success_callback,
                
                on_failure_callback=self.on_failure_callback,
                
                doc_md=self.doc_md,
                
                is_paused_upon_creation=self.is_paused_upon_creation,
                
                tags=self.tags,
                
                params=self.params,
                
                template_searchpath=self.template_searchpath,
                
                timezone=self.timezone
            )
            return dag

        except Exception as erro:
            logging.error(f"Error creating DAG: {erro}")
            raise
