# GKE Deployment Guide

## Prerequisites

1. **GKE Cluster** — Create if you don't have one:
```bash
gcloud container clusters create finops-cluster \
  --zone=asia-south1-a \
  --num-nodes=2 \
  --machine-type=e2-standard-2 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=3 \
  --project=ssh-marine
```

2. **Artifact Registry** — Create repo:
```bash
gcloud artifacts repositories create finops-reports \
  --repository-format=docker \
  --location=asia-south1 \
  --project=ssh-marine
```

3. **NGINX Ingress Controller** — Install if not present:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

## One-Time Setup

### 1. Encode GCP Service Account Key
```bash
base64 -w 0 credentials/gcp-sa.json
```

Copy the output and paste it into `k8s/secret.yaml` under `data.gcp-sa.json`.

### 2. Update Secret Values
Edit `k8s/secret.yaml` and fill in:
- Email credentials (if using email notifications)
- Slack webhook (if using Slack)
- Any other environment-specific values

### 3. Apply Secrets
```bash
kubectl apply -f k8s/secret.yaml
```

### 4. Deploy Application
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

### 5. Get Ingress IP
```bash
kubectl get ingress -n finops
```

Wait for the `ADDRESS` column to show an external IP (takes 2-5 minutes).

## Access Application

Once the ingress has an external IP:

- **Frontend**: `http://<INGRESS_IP>/ssh-gcp-costing/`
- **Backend API**: `http://<INGRESS_IP>/ssh-gcp-costing-backend/health`
- **API Docs**: `http://<INGRESS_IP>/ssh-gcp-costing-backend/docs`

## Cloud Build Setup

### 1. Update Substitutions
In `cloudbuild.yaml`, update:
```yaml
substitutions:
  _CLUSTER_NAME: your-gke-cluster  # Your actual cluster name
  _CLUSTER_ZONE: asia-south1-a     # Your cluster zone
```

### 2. Grant Cloud Build Permissions
```bash
# Get Cloud Build service account
PROJECT_NUMBER=$(gcloud projects describe ssh-marine --format='value(projectNumber)')
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Grant GKE access
gcloud projects add-iam-policy-binding ssh-marine \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/container.developer"

# Grant Artifact Registry access
gcloud projects add-iam-policy-binding ssh-marine \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/artifactregistry.writer"
```

### 3. Create Cloud Build Trigger
In GCP Console → Cloud Build → Triggers:
- Connect your repository
- Set trigger to run on push to `main` branch
- Use `weeklyreports/cloudbuild.yaml` as config file

## Manual Deployment

Build and push images:
```bash
cd weeklyreports

# Build backend
docker build -t asia-south1-docker.pkg.dev/ssh-marine/finops-reports/finops-backend:latest .

# Build frontend
docker build -t asia-south1-docker.pkg.dev/ssh-marine/finops-reports/finops-frontend:latest \
  -f frontend/Dockerfile.frontend \
  --build-arg VITE_API_URL=/ssh-gcp-costing-backend \
  frontend/

# Push images
docker push asia-south1-docker.pkg.dev/ssh-marine/finops-reports/finops-backend:latest
docker push asia-south1-docker.pkg.dev/ssh-marine/finops-reports/finops-frontend:latest

# Restart deployments
kubectl rollout restart deployment/finops-backend -n finops
kubectl rollout restart deployment/finops-frontend -n finops
```

## Useful Commands

```bash
# Check pod status
kubectl get pods -n finops

# View logs
kubectl logs -f deployment/finops-backend -n finops
kubectl logs -f deployment/finops-frontend -n finops

# Describe pod (for troubleshooting)
kubectl describe pod <pod-name> -n finops

# Scale deployment
kubectl scale deployment/finops-backend --replicas=2 -n finops

# Delete everything
kubectl delete namespace finops
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n finops
kubectl logs <pod-name> -n finops
```

### Ingress not getting IP
```bash
kubectl describe ingress finops-ingress -n finops
kubectl get svc -n ingress-nginx
```

### Image pull errors
```bash
# Verify Artifact Registry permissions
gcloud artifacts repositories get-iam-policy finops-reports \
  --location=asia-south1
```
