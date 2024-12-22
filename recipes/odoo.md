This recipe outlines how you can migrate an Odoo Docker instance into a Kubernetes cluster.
It involves following sub-systems:

1. k0s based Kubernetes cluster.
2. Longhorn for persistent-volumes.
3. k9s as cluster overview
4. kubectl, k as client to the cluster

This recipe aims to help you run Odoo in a High Availability (HA) mode, which means, if one instance goes down, users will continue to be able access the service, albiet at a slightly reduced speed.

If you are new to Kubernetes, read the basics here, and there's lots of useful information on the web and YouTube, not to mention your favourite LLM based AI-chatbot!

## Baseline Situation

You should be using this recipe if your current situaion is as follows:

1. You are running Odoo on Dockers on Linux VMs or Baremetal.
2. You are using the Linux host for persistent volumes. This means, you are storing some or all the below on the VM/Baremetal:

    - PostgreSQL database files
    - /etc/ folder
    - /addons/ folder
    - Odoo's log files

    And these are being mounted into the Docker-Container in runtime.

3. Your team uses Git to push code from their dev-environments, and pull via CLI on run-environments (staging, production and maybe others).

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

## Copy the odoo data and the postgresql database to the rec1 (pick an other machine is okay) machine
- find all the volume from the containers: docker inspect ...
- Copy odoo data: using scp or some tools that you familiar with
- take and Copy sql database backup or the postgresql database folder

```
## Get the docker volumes
docker inspect ...

#Example
scp -r /var/lib/docker/volumes/simplify-erp14_odoo-web-data/_data root@88.99.145.186:/data/commercecore/odoo-data

## Backup postgresql database
pg_dump -U odoo -d commercecore > commercecore.sql

scp commercecore-all.sql root@88.99.145.186:/data/commercecore/postgre

```

## Copy the data in rec1 (or other machine) machine into the pods
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
- Edit local /etc/hosts file and make sure the app is deployed correctly

## Copy the image to other nodes
- This step will copy the local docker image for example 127.0.0.1:5000/odoo-commercecore:commit-1 (IMAGE_NAME in the building step) to other nodes in the cluster
- action those commands

```
## Save the docker image
sudo docker image save 127.0.0.1:5000/odoo-kj:commit-1 > odoo-kj.tar
## Copy to other nodes
scp odoo-kj.tar tan@88.99.145.186:/home/tan/build-image

## ssh to orther nodes 
ssh tan@88.99.145.186
## Load docker image
sudo docker load < odoo-kj.tar

## Push to local registry
sudo docker push 127.0.0.1:5000/odoo-kj:commit-1
```

## Scale replicas in the deployment yaml
- Edit the replicas factor in the odoo deployment yaml file from 1 to 2 => ensure HA
- 

## Enable TLS with ingress-nginx and cert-manager
Create an issuer file:
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer # I'm using ClusterIssuer here
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: <your-email-address>
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: traefik 
```
If you already created this, you can skip

Expose a deployment via a service:

```
apiVersion: v1
kind: Service
metadata:
  name: odoo
  namespace: tyroled
spec:
  ports:
    - name: http
      port: 8069
      targetPort: 8069
    - name: longpolling
      port : 8072
      targetPort: 8072
  selector:
    app: odoo
```

In this case odoo app is exposed via port 8069. Make sure when defining an ingress, port to be exposed via ingress must corresponds to exposed service port:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tyroled-ingress
  namespace: tyroled
spec:
  ingressClassName: nginx
  rules:
  - host: tyroled.simplify-erp.de
    http:
      paths:
      - backend:
          service:
            name: odoo
            port:
              number: 8069
        path: /
        pathType: Prefix
  tls:
  - hosts:
    - tyroled.simplify-erp.de
    secretName: tyroled-tls
status:
  loadBalancer:
    ingress:
    - ip: 88.99.162.52
```
In addition, ask your admin for changing DNS record of domain you want to apply into.
You may want to define a secret file to get TLS certificate:

```
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: tyroled-tls
  namespace: tyroled
spec:
  dnsNames:
    - tyroled.simplify-erp.de
  secretName: tyroled-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
```
