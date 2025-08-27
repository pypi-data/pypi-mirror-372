from setuptools import setup, find_packages

setup(
    name="airflow_model",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "apache-airflow>=2.7.0,<4.0",
        "apache-airflow-providers-postgres>=6.2.3,<7.0",
        "apache-airflow-providers-google>=17.1.0,<18.0",
        "apache-airflow-providers-amazon>=6.0.0,<7.0",
        "apache-airflow-providers-sqlite>=3.0.0,<4.0",
        "apache-airflow-providers-http>=4.0.0,<5.0",

        "pandas>=2.0.0",
        "numpy>=1.25.0",
        "matplotlib>=3.8.0",
        "scipy>=1.12.0",
        "sqlalchemy>=1.4.36,<2.0.0",

        "flask>=2.2.2,<2.3.0",
        "requests>=2.32.0",
        "fastapi>=0.116.0",

        "python-dotenv>=1.1.0",
        "psycopg2-binary>=2.9.0",
        "jinja2>=3.1.0"
    ],
    python_requires=">=3.11,<3.12",
    description="Custom Python library to simplify creation of Airflow DAGs",
    author="Pedro Henrique Quaiato",
    url="https://github.com/seuusuario/airflow_model",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Apache Airflow",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)
