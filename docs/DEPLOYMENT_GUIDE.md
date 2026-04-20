# 🚀 AI Tutor Platform: Deployment Guide

This guide provides exact commands to set up, deploy, and manage the AI Tutor Platform on a Kubernetes KIND cluster.

## 📋 Prerequisites

Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [KIND](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

---

## 🛠 Step-by-Step Deployment

### 1. Create KIND Cluster
Use the provided multi-node configuration:
```bash
kind create cluster --config kind-config.yaml --name ai-tutor-cluster
```

### 2. Configure Environment & Secrets
Create the namespace first:
```bash
kubectl apply -f k8s/namespace.yaml
```
Apply your Groq API Key as a secret:
```bash
kubectl create secret generic ai-tutor-secret \
  --from-literal=GROQ_API_KEY=your_actual_key_here \
  -n ai-tutor --dry-run=client -o yaml | kubectl apply -f -
```

### 3. Build and Load Docker Image
Build the production image locally:
```bash
docker build -t ai-tutor-app:latest .
```
Load the image into the KIND control plane and worker nodes:
```bash
kind load docker-image ai-tutor-app:latest --name ai-tutor-cluster
```

### 4. Apply Kubernetes Manifests
Apply all resources in order:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/networkpolicy.yaml
```

### 5. Verify Deployment
Monitor the rollout status:
```bash
kubectl rollout status deployment/ai-tutor-app -n ai-tutor
```
Check pods and storage:
```bash
kubectl get pods -n ai-tutor
kubectl get pvc -n ai-tutor
```

### 6. Access the Application
For local testing without a real Ingress controller:
```bash
kubectl port-forward svc/ai-tutor-service -n ai-tutor 8501:80
```
Open your browser at `http://localhost:8501`.

---

## 🔄 Management & Maintenance

### Update Deployment
After making code changes:
```bash
docker build -t ai-tutor-app:v2 .
kind load docker-image ai-tutor-app:v2 --name ai-tutor-cluster
kubectl set image deployment/ai-tutor-app ai-tutor=ai-tutor-app:v2 -n ai-tutor
```

### Rollback
If something goes wrong:
```bash
kubectl rollout undo deployment/ai-tutor-app -n ai-tutor
```

### Cleanup
Delete the entire cluster:
```bash
kind delete cluster --name ai-tutor-cluster
```

---
**Senior DevOps Tip**: Always use versioned tags (e.g., `v1.0.1`) instead of `latest` in production to ensure deterministic rollbacks!
