from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.email import EmailOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

from datetime import datetime, timedelta
from scripts.functions import download_rates, get_slack_notification

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
    
    is_forex_rates_available = HttpSensor(
        task_id= "is_forex_rates_available",
        http_conn_id= "forex_api",
        endpoint= "marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b",
        response_check= lambda resp: "rates" in resp.text,
        poke_interval= 5,
        timeout= 20 # After 20sec of unsuccess, the task fails
    )

    is_forex_currencies_file_available = FileSensor(
        task_id= "is_forex_currencies_file_available",
        fs_conn_id= "forex_path",
        filepath= "forex_currencies.csv",
        poke_interval= 5,
        timeout= 20
    )

    downloading_rates = PythonOperator(
        task_id= "downloading_rates",
        python_callable= download_rates
    )

    saving_rates = BashOperator(
        task_id= "saving_rates",
        bash_command= """
            hdfs dfs -mkdir -p /forex && \
            hdfs dfs -put -f $AIRFLOW_HOME/dags/files/forex_rates.json /forex
        """
    )

    creating_forex_rates_table = HiveOperator(
        task_id="creating_forex_rates_table",
        hive_cli_conn_id="hive_conn",
        hql="""
            CREATE EXTERNAL TABLE IF NOT EXISTS forex_rates(
                base STRING,
                last_update DATE,
                eur DOUBLE,
                usd DOUBLE,
                nzd DOUBLE,
                gbp DOUBLE,
                jpy DOUBLE,
                cad DOUBLE
                )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """
    )

    forex_processing = SparkSubmitOperator(
        task_id= "forex_processing",
        application= "/opt/airflow/dags/scripts/forex_processing.py",
        conn_id= "spark_conn",
        verbose= False
    )

    # send_email_notification = EmailOperator(
    #     task_id= "send_email_notification",
    #     to= "airflow_course@yopmail.com",
    #     subject= "forex_data_pipeline",
    #     html_content="<h3>forex_data_pipeline</h3>"
    # )

    send_slack_notification = SlackWebhookOperator(
        task_id= "send_slack_notification",
        http_conn_id="slack_conn",
        message= get_slack_notification(),
        channel="#monitoring"
    )


    is_forex_rates_available \
        >> is_forex_currencies_file_available \
        >> downloading_rates \
        >> saving_rates \
        >> creating_forex_rates_table \
        >> forex_processing \
        >> send_slack_notification  
    
    
    


