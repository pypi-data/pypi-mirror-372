from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="airflow-model",
    version="0.4.0",  
    packages=find_packages(),
    install_requires=[
        "apache-airflow>=2.7.0,<4.0",
        "apache-airflow-providers-postgres",
        "apache-airflow-providers-google",
        "apache-airflow-providers-amazon",
        "apache-airflow-providers-sqlite",
        "apache-airflow-providers-http",

        "pandas>=2.0.0",
        "numpy>=1.25.0",
        "matplotlib>=3.8.0",
        "scipy>=1.12.0",
        "sqlalchemy>=1.4.36,<2.0",  

        "flask>=2.3.0",
        "requests>=2.32.0",
        "fastapi>=0.116.0",

        "python-dotenv>=1.1.0",
        "psycopg2-binary>=2.9.0",
        "jinja2>=3.1.0"
    ],
    python_requires=">=3.11",
    description="Custom Python library to simplify creation of Airflow DAGs and tasks",
    author="Pedro Henrique Quaiato",
    url="https://github.com/seuusuario/airflow-model",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Apache Airflow",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)
