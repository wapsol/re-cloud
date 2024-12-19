
IMAGE_NAME=127.0.0.1:5000/odoo-commercecore:commit-1
sudo docker build . --tag $IMAGE_NAME
sudo docker push $IMAGE_NAME
