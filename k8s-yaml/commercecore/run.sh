
IMAGE_NAME=127.0.0.1:5000/odoo-commercecore:commit-1
sudo docker build . --tag $IMAGE_NAME
sudo docker push $IMAGE_NAME


## save and copy the docker images
sudo docker image save 127.0.0.1:5000/odoo-kj:commit-1 > odoo-kj.tar
scp odoo-kj.tar tan@88.99.145.186:/home/tan/build-image

## dump and restore database postgres
pg_dump -U odoo -d kj-dev > kj-dev.sql
psql -U odoo -d kj-dev < kj-dev.sql 


