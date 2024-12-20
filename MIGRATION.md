# Migration process with Longhorn volume and running Odoo in multi-instance mode (HA Mode)

## First apply the Odoo and PostgreSQL instances
- edit the name of the yaml files follow with the name of the app we want to migrate
- Edit the postgresql and odoo versions so that it match the app (example odoo:18, postgresql:17)
- use commercecore as a template
- Apply all the resources with kubectl tool

```
## Edit the name commercecore 
cd k8s-yaml/commercecore/postgresql
k apply -f .

cd k8s-yaml/commercecore/odoo
k apply -f .

```

## Copy the odoo data and the postgresql database to the rec1 machine
- Copy odoo data: using scp or some tools that you familiar with
- take and Copy sql database backup or the postgresql database folder

```
#Example
scp -r /var/lib/docker/volumes/simplify-erp14_odoo-web-data/_data root@88.99.145.186:/data/commercecore/odoo-data

## Backup postgresql database
pg_dump -U odoo -d commercecore > commercecore.sql

scp commercecore-all.sql root@88.99.145.186:/data/commercecore/postgre


```

## Copy the data in rec1 machine into the pods
- Using the kubectl tool to copy the data in to the pods

```
## again edit the pod and namespace name follow the migration app 
kubectl cp -n commercecore . <pod_name>:/var/lib/odoo/

## Copy postgre sql to the pods
kubectl cp -n commercecore serp_09_12.sql commercecore-postgre-9d95c6484-5qtsz:/var/lib/postgresql
## Action restore postgresql
psql -U odoo -d commercecore < commercecore.sql 

```

## Build local docker image
- create Dockerfile right in the folder which contains the add-on folder, here is and example

```
# Dockerfile

FROM odoo:<edit-the-version-follow-the-app>

COPY --chown=odoo addons /mnt/extra-addons
COPY --chown=odoo enterprise /mnt/enterprise
<Add more COPY actions here if there are mores add-on folder to run>

```

- Run docker build and push image to local registry

```
## Run those commands to build the image 
IMAGE_NAME=127.0.0.1:5000/odoo-commercecore:commit-1
sudo docker build . --tag $IMAGE_NAME
sudo docker push $IMAGE_NAME

```


## Restart the Odoo deployments and apply the ingress and tls cert creation
- Change the image name the odoo deployment.yaml files
- from odoo:18 -> 127.0.0.1:5000/odoo-commercecore:commit-1 (IMAGE_NAME in the building step)

```
## Restart to deployment Odoo
kubectl rollout restart deployment -n <namespace_follow_app_name> <deployment_follow_app_name> 

cd k8s-yaml/commercecore
kubectl apply -f ingress.yaml
```

## Verify status of the app
