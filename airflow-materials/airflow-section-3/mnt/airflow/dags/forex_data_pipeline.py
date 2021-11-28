from datetime import datetime, timedelta
from airflow import DAG
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor

from datetime import datetime, timedelta

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
    
    is_forex_rates_available = HttpSensor (
        task_id= "is_forex_rates_available",
        http_conn_id= "forex_api",
        endpoint= "marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b",
        response_check= lambda resp: "rates" in resp.text,
        poke_interval= 5,
        timeout= 20 # After 20sec of unsuccess, the task fails
    )









    