# Migrating Odoo from Docker to Kubernetes

This recipe guides you through migrating an Odoo Docker instance to a Kubernetes cluster with High Availability (HA) configuration.

Following systems-components are involved.

1. Kubernetes
   1. Pods containing Odoo and PostgreSQL containers
   2. Persistent Volume Claims (PVCs) to Longhorn PS.
2. Longhorn Persistent Storage
3. Harbor Container Repository

## Prerequisites

### Required Components
- `k0s` - Kubernetes distribution
- `longhorn` - Storage solution for persistent volumes
- `k9s` - Cluster management UI
- `kubectl` (alias `k`) - Kubernetes command-line tool

### Initial Setup Requirements
1. Running Odoo on Docker (Linux VM or Baremetal)
2. Persistent volumes on Linux host for:
   - PostgreSQL database files
   - `/etc/` configuration
   - `/addons/` directory
   - Odoo log files
3. Git-based deployment workflow

### Current Architecture
![image](https://github.com/user-attachments/assets/50274eaa-61ea-4c42-9fd5-9701530b19a3)

## Migration Steps

### 1. Backup Docker Environment

1. Back up Docker images:
   ```bash
   # Save Docker images (oad1, opd1)
   sudo docker image save 127.0.0.1:5000/odoo-kj:commit-1 > odoo-kj.tar
   ```

2. Back up persistent volumes (pvo1, pvp1)

### 2. Transfer to Cluster Nodes

1. Copy Docker images to cluster nodes:
   ```bash
   # Copy image to other nodes
   scp odoo-kj.tar user@node-ip:/home/user/build-image

   # On target node:
   sudo docker load < odoo-kj.tar
   sudo docker push 127.0.0.1:5000/odoo-kj:commit-1
   ```

### 3. Prepare Kubernetes Deployment

1. Configure and apply PostgreSQL resources:
   ```bash
   cd k8s-yaml/[app-name]/postgresql
   kubectl apply -f .
   ```

2. Configure and apply Odoo resources:
   ```bash
   cd k8s-yaml/[app-name]/odoo
   kubectl apply -f .
   ```

### 4. Data Migration

1. Copy Odoo data:
   ```bash
   # Example data transfer
   scp -r /var/lib/docker/volumes/[volume-name]/_data root@node-ip:/data/[app-name]/odoo-data
   ```

2. Migrate PostgreSQL database:
   ```bash
   # Backup database
   pg_dump -U odoo -d [dbname] > [dbname].sql

   # Copy to target node
   scp [dbname].sql root@node-ip:/data/[app-name]/postgre

   # Copy into pod
   kubectl cp -n [namespace] [dbname].sql [pod-name]:/var/lib/postgresql
   
   # Restore database
   psql -U odoo -d [dbname] < [dbname].sql
   ```

### 5. Build Kubernetes-Ready Docker Image

1. Create Dockerfile:
   ```dockerfile
   FROM odoo:[version]

   COPY --chown=odoo addons /mnt/extra-addons
   COPY --chown=odoo enterprise /mnt/enterprise
   ```

2. Build and push image:
   ```bash
   IMAGE_NAME=127.0.0.1:5000/odoo-[app-name]:commit-1
   sudo docker build . --tag $IMAGE_NAME
   sudo docker push $IMAGE_NAME
   ```

### 6. Deploy to Kubernetes

1. Update deployment configuration:
   - Update image reference in deployment YAML
   - Scale replicas for HA (minimum 2)

2. Apply changes:
   ```bash
   kubectl rollout restart deployment -n [namespace] [deployment-name]
   kubectl apply -f ingress.yaml
   ```

### 7. Configure TLS and Ingress

1. Create ClusterIssuer:
   ```yaml
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-prod
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: [your-email]
       privateKeySecretRef:
         name: letsencrypt-prod
       solvers:
       - http01:
           ingress:
             class: traefik
   ```

2. Configure Service:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: odoo
     namespace: [namespace]
   spec:
     ports:
       - name: http
         port: 8069
         targetPort: 8069
       - name: longpolling
         port: 8072
         targetPort: 8072
     selector:
       app: odoo
   ```

3. Configure Ingress:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: [app-name]-ingress
     namespace: [namespace]
   spec:
     ingressClassName: nginx
     rules:
     - host: [your-domain]
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: odoo
               port:
                 number: 8069
     tls:
     - hosts:
       - [your-domain]
       secretName: [app-name]-tls
   ```

4. Configure TLS Certificate:
   ```yaml
   apiVersion: cert-manager.io/v1
   kind: Certificate
   metadata:
     name: [app-name]-tls
     namespace: [namespace]
   spec:
     dnsNames:
       - [your-domain]
     secretName: [app-name]-tls
     issuerRef:
       name: letsencrypt-prod
       kind: ClusterIssuer
   ```

### 8. Final Configuration

1. Update DNS records for your domain
2. Verify deployment status
3. Test application functionality

## Notes
- Replace placeholders (marked with `[]`) with your actual values
- Ensure proper backups before migration
- Test in a staging environment first
- Monitor system during and after migration

