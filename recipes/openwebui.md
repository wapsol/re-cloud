# Installing OpenWebUI with Ollama Backend on re-cloud/Kubernetes

This guide provides a step-by-step recipe to install OpenWebUI (with Ollama as its backend) on the [re-cloud/Kubernetes](https://re-cloud.io/kubernetes/) cluster. re-cloud uses [Longhorn](https://longhorn.io/) as its persistent storage solution, configure an Ingress for the domain `https://chat.mydomain.de`, and secure it with an SSL certificate via Cert-Manager (Let’s Encrypt).

> **Disclaimer**  
> This guide is intended as a reference. Adjust configuration details, namespaces, storage classes, and domain names to match your environment. If you already have certain prerequisites in place (e.g., an Ingress controller, Cert-Manager, or other custom resources), you can skip or modify the relevant steps.

---

## Prerequisites

1. **re-cloud/Kubernetes**: A running [Kubernetes](https://re-cloud.io/kubernetes/) cluster with at least one worker node.  
2. **Storage**: [Longhorn](https://re-cloud.io/longhorn/) installed and configured as the default storage class (or an alternative storage class ready).  
3. **Domain Name**: You own `mydomain.de` and can create a DNS record `chat.mydomain.de` pointing to the load balancer or node IP where the Ingress controller is running.  
4. **Ingress Controller**: An Ingress controller (e.g., Nginx Ingress) is installed in the cluster.  
5. **Cert-Manager (Optional)**: For automated SSL certificate provisioning via Let’s Encrypt.

---

## Overview

1. **Create a Namespace**: `openwebui`.
2. **Deploy Ollama**: Run Ollama in a container with persistent storage (Longhorn).
3. **Deploy OpenWebUI**: Configure it to point to the Ollama backend.
4. **Set Up Ingress**: Expose OpenWebUI at `chat.mydomain.de` with SSL.
5. **Test**: Verify access over HTTPS.

---

## 1. Create the `openwebui` Namespace

Create a dedicated namespace for all resources:

```bash
kubectl create namespace openwebui
```

---

## 2. (Optional) Install Cert-Manager

If you haven’t installed Cert-Manager, do so to manage SSL certificates automatically.

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
```

Wait until all Cert-Manager pods are in the `Running` state:

```bash
kubectl get pods --namespace cert-manager
```

---

## 3. Set Up Longhorn (If Not Already Installed)

1. Ensure Longhorn is installed. ([Quickstart Guide](https://longhorn.io/docs/1.3.2/deploy/install/install-with-kubectl/))
2. Verify `StorageClass` is created:
   ```bash
   kubectl get storageclass
   ```
   Ensure there is a Longhorn storage class (for example `longhorn`), which you can set as default if desired.

---

## 4. Deploy the Ollama Backend

### 4.1 Create a Persistent Volume Claim

Below is an example YAML creating a 10Gi PVC named `ollama-pvc` using the Longhorn storage class:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ollama-pvc
  namespace: openwebui
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 10Gi
```

Apply it:
```bash
kubectl apply -f ollama-pvc.yaml
```

### 4.2 Create the Ollama Deployment and Service

In this example, we assume there is a container image for Ollama called `ghcr.io/jmorganca/ollama:latest`. Adjust to the correct image if needed.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: openwebui
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ghcr.io/jmorganca/ollama:latest
        ports:
        - containerPort: 11411
        volumeMounts:
        - name: ollama-data
          mountPath: /data # Adjust if the Ollama image expects a different path
      volumes:
      - name: ollama-data
        persistentVolumeClaim:
          claimName: ollama-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
  namespace: openwebui
spec:
  selector:
    app: ollama
  ports:
  - name: http
    port: 11411
    targetPort: 11411
    protocol: TCP
```

Apply it:
```bash
kubectl apply -f ollama-deployment.yaml
```

> **Note**:  
> - Ollama will listen on port `11411` by default (check official documentation or the Docker image details for the correct port).  
> - The volumes should match how Ollama’s Docker image expects data and/or model storage. Adjust path and size as needed.  

---

## 5. Deploy OpenWebUI

### 5.1 Create a Persistent Volume Claim (Optional)

If OpenWebUI requires storage (e.g. for caching, logs, etc.), create a separate PVC:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: openwebui-pvc
  namespace: openwebui
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 5Gi
```

Apply it:
```bash
kubectl apply -f openwebui-pvc.yaml
```

### 5.2 Create the OpenWebUI Deployment and Service

In this example, we assume OpenWebUI’s Docker image is `ghcr.io/openwebui/openwebui:latest`. Adjust as needed.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openwebui
  namespace: openwebui
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openwebui
  template:
    metadata:
      labels:
        app: openwebui
    spec:
      containers:
      - name: openwebui
        image: ghcr.io/openwebui/openwebui:latest
        env:
        - name: OLLAMA_URL
          value: "http://ollama-service.openwebui.svc.cluster.local:11411"
          # The environment variable name & usage can vary. Adjust to match OpenWebUI config.
        ports:
        - containerPort: 7860  # Example OpenWebUI port
        volumeMounts:
        - name: openwebui-data
          mountPath: /app/data  # Adjust if needed
      volumes:
      - name: openwebui-data
        persistentVolumeClaim:
          claimName: openwebui-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: openwebui-service
  namespace: openwebui
spec:
  selector:
    app: openwebui
  ports:
  - name: http
    port: 80
    targetPort: 7860
    protocol: TCP
```

Apply it:
```bash
kubectl apply -f openwebui-deployment.yaml
```

> **Note**:  
> - Check the official OpenWebUI documentation for correct environment variables to configure the Ollama backend.  
> - The container port `7860` is used as an example. Adjust if OpenWebUI listens on a different port.  

---

## 6. Create an Ingress for SSL (Let’s Encrypt)

If you have Cert-Manager and an Ingress controller (e.g., Nginx Ingress), you can create an Ingress resource that automatically provisions an SSL certificate for `chat.mydomain.de`.

> **Important**: Ensure that you have a ClusterIssuer or Issuer configured for Let’s Encrypt. Replace `letsencrypt-prod` with the name of your configured issuer.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openwebui-ingress
  namespace: openwebui
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - chat.mydomain.de
    secretName: openwebui-tls
  rules:
  - host: chat.mydomain.de
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: openwebui-service
            port:
              number: 80
```

Apply it:
```bash
kubectl apply -f openwebui-ingress.yaml
```

Within a few minutes (depending on your issuer’s ACME DNS challenge/HTTP challenge setup), you should have a valid certificate, and you can access OpenWebUI at:

```
https://chat.mydomain.de
```


## 7. Validation

1. **Check Pods**:  
   ```bash
   kubectl get pods -n openwebui
   ```
   Ensure both `ollama` and `openwebui` pods are in `Running` state.

2. **Check Services**:  
   ```bash
   kubectl get svc -n openwebui
   ```
   Confirm the services are exposing the correct ports.

3. **Check Ingress**:  
   ```bash
   kubectl get ingress -n openwebui
   ```
   Confirm the address/hosts are populated correctly and the TLS secret has been issued.

4. **DNS**: Make sure your DNS `chat.mydomain.de` is pointing to your cluster’s Ingress Controller IP or load balancer IP.

5. **Browser Test**: Open a web browser and navigate to:
   ```
   https://chat.mydomain.de
   ```
   You should see the OpenWebUI interface. Interacting with the UI should route requests to the Ollama backend.

---

## 8. Troubleshooting

1. **Ingress Not Resolving**: Check DNS settings. Ensure `chat.mydomain.de` points to the correct IP or load balancer.
2. **SSL Certificate Not Issued**:
   - Check Cert-Manager logs: `kubectl logs -n cert-manager deploy/cert-manager`
   - Verify that your ClusterIssuer is configured for Let’s Encrypt and that the ACME challenge is passing.
3. **Network Policies**: If you have network policies, ensure traffic is allowed between the OpenWebUI pod and the Ollama service.

---

## References and Further Reading

- **k0s Documentation**: [https://docs.k0sproject.io/](https://docs.k0sproject.io/)
- **Longhorn**: [https://longhorn.io/](https://longhorn.io/)
- **Ollama**: [https://github.com/jmorganca/ollama](https://github.com/jmorganca/ollama)
- **OpenWebUI**: [https://github.com/xusenlinzy/OpenWebUI](https://github.com/xusenlinzy/OpenWebUI)
- **Cert-Manager**: [https://cert-manager.io/docs/](https://cert-manager.io/docs/)

---

**Congratulations!** You have successfully deployed OpenWebUI with Ollama as its backend on k0s, using Longhorn for persistent storage, and exposed it securely via HTTPS at `https://chat.mydomain.de`.  
