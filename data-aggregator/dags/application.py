from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


with DAG("application_pipelineV2",
         start_date=datetime(2025,11,22),
         schedule="@weekly"
):
    # create_cv = PythonOperator(
    #     task_id="generate_cv",
    #     python_callable=generate_resume
    # )

    # create_cv
    pass

