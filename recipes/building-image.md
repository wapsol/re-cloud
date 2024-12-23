# This recipe outlines how you can build the Odoo application with custom addons and deploy it in the k0s cluster

## Step 1: Ensure Dockerfile is present
- Edit the Dockerfile based on what your Odoo application requires including addons folder and maybe python libraries

## Step 2: Run docker build and push to container registry
- Run the build in your local machine or in the server
- This step requires login to the container registry firsts

```bash
IMAGE_NAME=crepo.re-cloud.io/re-cloud/odoo-<your_app_name>:<tag_version or commit_id>
sudo docker build . -tag $IMAGE_NAME
sudo docker push $IMAGE_NAME
```

## Step 3: Edit and deploy the deployment yaml file
- Change image spec to the new image name
- Apply file with kubectl

```bash
kubectl apply -f odoo/deployment.yaml
```