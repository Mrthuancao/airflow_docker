from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def push_value():
    return 'Hello, Airflow!'

def pull_value(**context):
    value = context['task_instance'].xcom_pull(task_ids='push_value')
    print(value)

default_args = {
    'start_date': datetime(2024, 5, 10)
}

dag = DAG('xcom_example_dag', default_args=default_args, schedule_interval=None)

push_task = PythonOperator(
    task_id='push_value',
    python_callable=push_value,
    dag=dag
)

pull_task = PythonOperator(
    task_id='pull_value',
    python_callable=pull_value,
    provide_context=True,
    dag=dag
)

push_task >> pull_task