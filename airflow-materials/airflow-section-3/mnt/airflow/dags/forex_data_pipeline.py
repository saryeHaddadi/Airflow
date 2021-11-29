from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta

from scripts.forex_download import download_rates

tasks_default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email": "sarye@live.fr",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(dag_id= "forex_data_pipeline",
         start_date= datetime(2021, 11, 1),
         schedule_interval= "@daily",
         catchup= False,
         default_args= tasks_default_args) as dag:
    
    is_forex_rates_available= HttpSensor (
        task_id= "is_forex_rates_available",
        http_conn_id= "forex_api",
        endpoint= "marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b",
        response_check= lambda resp: "rates" in resp.text,
        poke_interval= 5,
        timeout= 20 # After 20sec of unsuccess, the task fails
    )

    is_forex_currencies_file_available= FileSensor (
        task_id= "is_forex_currencies_file_available",
        fs_conn_id= "forex_path",
        filepath= "forex_currencies.csv",
        poke_interval= 5,
        timeout= 20
    )

    downloading_rates= PythonOperator(
        task_id= "downloading_rates",
        python_callable= download_rates
    )







