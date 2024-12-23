# How to deploy Harbor

## Install certbot first for let's encrypt ssl

```bash
apt install certbot -y
```

- generate cert (remember dns domain need to be resolvable)

```bash
certbot certonly --standalone -d crepo.re-cloud.io
```

```bash
cp /etc/letsencrypt/live/crepo.re-cloud.io/fullchain.pem /etc/harbor/cert/crepo.cert
cp /etc/letsencrypt/live/crepo.re-cloud.io/privkey.pem /etc/harbor/cert/crepo.key
```

- Create renew-post hook

```bash
## create shell script and put it into: /etc/letsencrypt/renewal-hooks/post/harbor.sh

#!/bin/bash

cp /etc/letsencrypt/live/crepo.re-cloud.io/fullchain.pem /etc/harbor/cert/crepo.cert
cp /etc/letsencrypt/live/crepo.re-cloud.io/privkey.pem /etc/harbor/cert/crepo.key
/usr/bin/docker restart nginx

## dry-run test
certbot renew --dry-run
```

## Install harbor 

```bash
wget https://github.com/goharbor/harbor/releases/download/v2.11.2/harbor-offline-installer-v2.11.2.tgz
tar xvf harbor-offline-installer-v2.11.2.tgz
```

```bash
cd harbor
# edit config file 
vim harbor.yml

# Run install
./install.sh

```

## Create secret k8s for pulling image

```bash
kubectl create secret docker-registry -n <change_me> harbor-re-cloud --docker-server=https://crepo.re-cloud.io --docker-username=k0s-dev --docker-password=pU9hw~O6{G_Liw"]oo{\ --docker-email=k0s-dev@re-cloud.io


```