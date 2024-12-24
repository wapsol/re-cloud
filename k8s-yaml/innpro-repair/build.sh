export IMAGE_NAME=crepo.re-cloud.io/re-cloud/odoo-innpro-repair:commit-1
sudo docker build . --tag $IMAGE_NAME
sudo docker push $IMAGE_NAME