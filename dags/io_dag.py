from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def push_by_returning():
    return 'Return'

def no_target_push(**context):
    task_instance = context['task_instance']
    
    task_instance.xcom_push(key='my_key', value='No target')

# def targeted_push(**context):
#     task_instance = context['task_instance']
#     task_instance.xcom_push(key='my_key', value='Targeted', task_ids = ['pull_from_one', 'pull_from_multiple'])

def pull_from_one(**context):
    value = context['task_instance'].xcom_pull(key = 'my_key', task_ids='no_target_push')
    # print(vars(context['task_instance'].xcom_pull()))
    print(value)

# def pull_from_multiple(**context):
#     value1 = context['task_instance'].xcom_pull(task_ids='push_by_returning')
#     value2 = context['task_instance'].xcom_pull(key='my_key', task_ids='no_target_push')
#     print(value1, value2)

def pull_from_multiple(**context):
    values = context['task_instance'].xcom_pull(key=None, task_ids=['no_target_push', 'push_by_returning'])
    # value2 = context['task_instance'].xcom_pull(key='my_key', task_ids='no_target_push')
    print(values)



default_args = {
    'start_date': datetime(2024, 5, 10)
}

dag = DAG('xcom_push_and_pull_example_dag', default_args=default_args, schedule_interval=None)

push_by_returning_task = PythonOperator(
    task_id='push_by_returning',
    python_callable=push_by_returning,
    dag=dag
)

no_target_push_task = PythonOperator(
    task_id='no_target_push',
    python_callable=no_target_push,
    dag=dag
)

# targeted_push_task = PythonOperator(
#     task_id='targeted_push',
#     python_callable=targeted_push,
#     dag=dag
# )

pull_from_one_task = PythonOperator(
    task_id='pull_from_one',
    python_callable=pull_from_one,
    provide_context=True,
    dag=dag
)

pull_from_multiple_task = PythonOperator(
    task_id='pull_from_multiple',
    python_callable=pull_from_multiple,
    provide_context=True,
    dag=dag
)

# Define the task dependencies
push_by_returning_task >> pull_from_multiple_task
no_target_push_task >> [pull_from_one_task, pull_from_multiple_task]
# targeted_push_task >> [pull_from_one_task, pull_from_multiple_task]