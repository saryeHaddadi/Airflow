# VM Install

## Installing Airflow

Create and start a docker container from the Docker image python:3.8-slim and execute the command /bin/bash in order to have a shell session

> docker run -it --rm -p 8080:8080 python:3.8-slim /bin/bash

Print the Python version

> python -V

Export the environment variable AIRFLOW_HOME used by Airflow to store the dags folder, logs folder and configuration file

> export AIRFLOW_HOME=/usr/local/airflow

Check that the environment variable has been well exported

> env | grep airflow

Install all tools and dependencies that can be required by Airflow

> apt-get update -y && apt-get install -y wget libczmq-dev curl libssl-dev git inetutils-telnet bind9utils freetds-dev libkrb5-dev libsasl2-dev libffi-dev libpq-dev freetds-bin build-essential default-libmysqlclient-dev apt-utils rsync zip unzip gcc && apt-get clean

Create the user airflow, set its home directory to the value of AIRFLOW_HOME and log into it

> useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow

Show the file /etc/passwd to check that the airflow user has been created

> cat /etc/passwd | grep airflow

Upgrade pip (already installed since we use the Docker image python 3.5)

> pip install --upgrade pip

Log into airflow

> su - airflow

Create and activiate a virtual env named

> python -m venv .sandbox  
> source .sandbox/bin/activate

Download the requirement file to install the right version of Airflow’s dependencies
- /!\ Always install/update Airflow with a constrain file, this is very important.

> wget https://raw.githubusercontent.com/apache/airflow/constraints-2.0.2/constraints-3.8.txt
 
Install the version 2.0.2 of apache-airflow with all subpackages defined between square brackets. (Notice that you can still add subpackages after all, you will use the same command with different subpackages even if Airflow is already installed)

> pip install "apache-airflow[crypto,celery,postgres,cncf.kubernetes,docker]"==2.0.2 --constraint ./constraints-3.8.txt


Initialise the metadatabase
> airflow db init

Start Airflow’s scheduler in background
> airflow scheduler &

Start Airflow’s webserver in background
> airflow webserver &


# Docker Install

Build a docker image from the Dockerfile in the current directory (airflow-materials/airflow-basic)  and name it airflow-basic
> docker build -t airflow-basic .  
> docker run --rm -d -p 8080:8080 airflow-basic



##### Quick Tour of Airflow CLI

Show running docker containers
> docker ps

Execute the command /bin/bash in the container_id to get a shell session
> docker exec -it container_id /bin/bash

Print the current path where you are
> pwd

Initialise the metadatabase
> airflow db init

Reinitialize the metadatabase (Drop everything)
> airflow db reset

Upgrade the metadatabase (Latest schemas, values, ...)
> airflow db upgrade

Start Airflow’s webserver
> airflow webserver

Start Airflow’s scheduler
> airflow scheduler

Start a Celery worker (Useful in distributed mode to spread tasks among nodes - machines)
> airflow celery worker

Give the list of known dags (either those in the examples folder or in dags folder)
> airflow dags list

Display the files/folders of the current directory 
> ls

Trigger the dag example_python_operator with the current date as execution date
> airflow dags trigger example_python_operator

Trigger the dag example_python_operator with a date in the past as execution date (This won’t trigger the tasks of that dag unless you set the option catchup=True in the DAG definition)
> airflow dags trigger example_python_operator -e 2021-01-01

Trigger the dag example_python_operator with a date in the future (change the date here with one having +2 minutes later than the current date displayed in the Airflow UI). The dag will be scheduled at that date.
> airflow dags trigger example_python_operator -e '2021-01-01 19:04:00+00:00'

Display the history of example_python_operator’s dag runs
> airflow dags list-runs -d example_python_operator

List the tasks contained into the example_python_operator dag
> airflow tasks list example_python_operator

Allow to test a task (print_the_context) from a given dag (example_python_operator here) without taking care of dependencies and past runs. Useful for debugging.
> airflow tasks test example_python_operator print_the_context 2021-01-01
