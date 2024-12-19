# Migration process with Longhorn volume and running Odoo in multi-instance mode (HA Mode)

## First apply the Odoo and PostgreSQL instances
- edit the name of the yaml files follow with the name of the app we want to migrate
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
```

## Restart the Odoo deployments and apply the ingress and tls cert creation
```
## Restart to deployment Odoo
kubectl rollout restart deployment -n <namespace_follow_app_name> <deployment_follow_app_name> 

cd k8s-yaml/commercecore
kubectl apply -f ingress.yaml
```

## Verify status of the app
