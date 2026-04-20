# 🔍 AI Tutor Platform: Troubleshooting Guide

## 🚨 Common Issues & Solutions

### 1. Pods are in `CrashLoopBackOff`
- **Cause**: Often due to missing environment variables or volume mount failures.
- **Check**: `kubectl logs <pod-name> -n ai-tutor`
- **Check**: `kubectl describe pod <pod-name> -n ai-tutor`
- **Solution**: Ensure `GROQ_API_KEY` is correctly set in the Secret and that the `data/` directory is writable.

### 2. SQLite Database is Read-Only
- **Cause**: Incorrect file permissions in the container.
- **Check**: `kubectl exec -it <pod-name> -n ai-tutor -- ls -l /app/data`
- **Solution**: The Dockerfile and Deployment are configured to run as user `1000`. Ensure the PVC is mounted with `fsGroup: 1000` (already set in `deployment.yaml`).

### 3. ChromaDB Initialization Errors
- **Cause**: Outdated SQLite version on the host image or corrupted index.
- **Solution**: The Dockerfile uses `python:3.11-slim` which includes compatible SQLite. If errors persist, delete the PVC and restart the pod to re-initialize the index (WARNING: This loses existing embeddings).

### 4. High Latency in Responses
- **Cause**: Network bottleneck or LLM rate limiting.
- **Solution**: Check the `Groq` dashboard for rate limit status. Monitor pod resources with `kubectl top pods -n ai-tutor`.

### 5. Ingress Not Accessible
- **Cause**: KIND cluster extra port mappings not applied or local `/etc/hosts` missing entry.
- **Solution**: 
    1. Verify cluster was created with `kind-config.yaml`.
    2. Add `127.0.0.1 ai-tutor.local` to your local machine's hosts file.
    3. Ensure an Ingress controller (like NGINX) is installed on the KIND cluster.

---

## 🛠 Useful Debugging Commands

**View Application Logs (Real-time):**
```bash
kubectl logs -f l/app=ai-tutor -n ai-tutor
```

**Inspect HPA Scaling Events:**
```bash
kubectl get hpa -n ai-tutor --watch
```

**Restart Deployment (Rolling):**
```bash
kubectl rollout restart deployment/ai-tutor-app -n ai-tutor
```

**Check Resource Usage:**
```bash
kubectl top pods -n ai-tutor
```

---
**Senior DevOps Tip**: In KIND, if you're hitting "ImagePullBackOff", remember to run `kind load docker-image ai-tutor-app:latest` so the cluster can see your local image!
