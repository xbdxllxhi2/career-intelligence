from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime



from cv_generator.generate_cv import generate_cv


with DAG("application_pipeline",
         start_date=datetime(2025,11,22),
         schedule="@weekly"
):
    create_cv = PythonOperator(
        task_id="generate_cv",
        python_callable=generate_cv
    )

    create_cv


