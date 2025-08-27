Airflow Model

Airflow Model is a Python library designed to simplify the creation and management of Apache Airflow DAGs, tasks, and database connections. It provides a modular approach for defining DAGs, tasks, and database hooks with customizable parameters.

Features

Modular DAG creation with full configuration options.

Task management for Python and Bash operators.

Database connection management for PostgreSQL with query execution from strings or files.

Extensible structure to add new operators or connections easily.

Installation

Install using pip:

pip install airflow-model


Ensure you have Python >= 3.11 and Apache Airflow 2.7.0+ installed in your environment.

Project Structure
airflow_model/
├── models/          # DAG, Task, and Connection models
├── constructors/    # DAG, Task, and Database constructors
├── __init__.py

Usage
1. Creating a DAG
from airflow_model.constructors.DagConstructor import DagConstructor

default_dag_params = {
    "name_dag": "example_dag",
    "start_date": "2025-08-26",
    "schedule": "0 6 * * *",
    "catchup": False,
    "tags": ["example", "demo"],
    "description": "An example DAG using Airflow Model"
}

dag_constructor = DagConstructor(default_dag_params)
dag = dag_constructor.construct_dag()

2. Creating Tasks
from airflow_model.constructors.TaskConstructor import TaskConstructor

default_task_params = [
    {
        "task_type": "python",
        "task_id": "hello_world",
        "python_callable": lambda: print("Hello, Airflow!"),
        "op_args": [],
        "op_kwargs": {}
    },
    {
        "task_type": "bash",
        "task_id": "print_date",
        "bash_command": "date"
    }
]

task_constructor = TaskConstructor()
tasks = task_constructor.configure_tasks(default_task_params)

3. Database Connection (PostgreSQL)

You can either pass a SQL string or use a SQL file.

SQL File Example

Create a SQL file: sql/query_users.sql

SELECT id, name, email
FROM users
WHERE active = TRUE;

Python Usage
from airflow_model.constructors.PostgresConstructor import PostgresConstructor

default_postgres_params = {
    "id_connection": "my_postgres_conn",
    "type_connection": "postgres",
    "string_query": None,                 # leave None to use file
    "path_file_query": "sql/query_users.sql",
    "permission_file_query": "r"
}

postgres_constructor = PostgresConstructor(default_postgres_params)
results = postgres_constructor.execute_query()

for row in results:
    print(row)


path_file_query: Path to the SQL file.

permission_file_query: File open mode, usually 'r'.

If string_query is provided, it overrides the file.

4. Full DAG Example with Tasks
from airflow_model.constructors.DagConstructor import DagConstructor
from airflow_model.constructors.TaskConstructor import TaskConstructor

# Define DAG
dag_params = {"name_dag": "demo_dag", "schedule": "@daily"}
dag_constructor = DagConstructor(dag_params)
dag = dag_constructor.construct_dag()

# Define Tasks
task_params = [
    {"task_type": "python", "task_id": "task_1", "python_callable": lambda: print("Task 1")},
    {"task_type": "bash", "task_id": "task_2", "bash_command": "echo Task 2"}
]

task_constructor = TaskConstructor()
tasks = task_constructor.configure_tasks(task_params)

# Set task dependencies
tasks[0]["task"] >> tasks[1]["task"]

License

This project is licensed under a Proprietary License.

You may use it internally and for personal projects.

Modification or commercial redistribution is not allowed.