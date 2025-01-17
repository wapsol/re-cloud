export IMAGE_NAME=crepo.re-cloud.io/airflow/custom-airflow:2.9.3
sudo docker build . --tag $IMAGE_NAME
sudo docker push $IMAGE_NAME