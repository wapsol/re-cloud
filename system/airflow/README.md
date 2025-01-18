# Guide on how to use Apache Airflow

This Airflow documentation is deployed using Helm chart, meaning it is capable of rolling back to previous revison whenever something's wrong(one of the features of Helm in Kubernetes environment). Please keep that in mind!

## Building image 
If you want to add some Python libraries to your Airflow deployment, it's better to create a Dockerfile like this:
```
FROM apache/airflow:2.9.3
COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
```
where requirements.txt is a file to define the libs you want to install, such as ```apache-airflow-providers-apache-kafka``` to integrate with Kafka.

## How to write a DAG for Airflow 

Assume you have access to our Kubernetes cluster, you can exec into the airflow-worker pod. It should be located in ```/opt/airflow/dags/repo```

How to exec:
![image](https://github.com/user-attachments/assets/a2049828-5f82-4aa2-95dd-314d7b53bcf5)
 
 Look for pods in namespace airflow and press ```s``` to exec into airflow-scheduler
 
 Write your own DAG file and put it into ```/opt/airflow/dags/repo```

 You may want to test it outside the Kubernetes environment first. If the testing work is done, copy the DAG into the pod:

 ```
kubectl cp example_dag.py -n airflow airflow-worker-0:/opt/airflow/dags/repo
```
 
