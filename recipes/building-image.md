# This recipe outlines how you can build the Odoo application with custom addons and deploy it in the k0s cluster

## Step 1: Sync source from local or pull change from git repo

- Sync source from local machine using rsync command

```bash
cd <source_dir>
rsync -avz . aliehvo@88.99.162.52:/home/aliehvo/<source_name_or_app_name>

```

- Pull change from git repository

```bash
ssh aliehvo@88.99.162.52
git clone <git_url>
cd <source_dir>
git pull

```
## Step 2: Ensure Dockerfile is present
- Edit the Dockerfile based on what your Odoo application requires including addons folder and maybe python libraries
- Make sure to put the Dockerfile in the <source_dir>

## Step 3: Run docker build and push to container registry
- Run the build in your local machine or in the server
- This step requires login to the container registry firsts

```bash
IMAGE_NAME=crepo.re-cloud.io/re-cloud/odoo-<your_app_name>:<tag_version or commit_id>
sudo docker build . --tag $IMAGE_NAME
sudo docker push $IMAGE_NAME
```

## Step 4: Edit and deploy the deployment yaml file
- Change image spec to the new image name
- Apply file with kubectl

```bash
kubectl apply -f odoo/deployment.yaml
```