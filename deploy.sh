#!/usr/bin/env bash
set -euo pipefail

# Deploy script for retailsense-ai to a Kubernetes cluster (or local k8s)
# Requirements: docker, kubectl, (optional) kind/minikube, and access to cluster

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Root: ${ROOT_DIR}"

echo "Building Docker images..."
docker build -t retailsense-backend:latest -f ${ROOT_DIR}/backend/Dockerfile ${ROOT_DIR}/backend
docker build -t retailsense-frontend:latest -f ${ROOT_DIR}/frontend/Dockerfile ${ROOT_DIR}/frontend

echo "Applying Kubernetes manifests..."
kubectl apply -f ${ROOT_DIR}/kubernetes/namespace.yaml
kubectl apply -f ${ROOT_DIR}/kubernetes/configmap.yaml -n retailsense
kubectl apply -f ${ROOT_DIR}/kubernetes/backend-deployment.yaml -n retailsense
kubectl apply -f ${ROOT_DIR}/kubernetes/backend-service.yaml -n retailsense
kubectl apply -f ${ROOT_DIR}/kubernetes/frontend-deployment.yaml -n retailsense
kubectl apply -f ${ROOT_DIR}/kubernetes/frontend-service.yaml -n retailsense
kubectl apply -f ${ROOT_DIR}/kubernetes/mlflow-deployment.yaml -n retailsense
kubectl apply -f ${ROOT_DIR}/kubernetes/mlflow-service.yaml -n retailsense
kubectl apply -f ${ROOT_DIR}/kubernetes/ingress.yaml -n retailsense

echo "Waiting for pods to be ready..."
kubectl wait --for=condition=available deployment/backend-deployment -n retailsense --timeout=120s || true
kubectl wait --for=condition=available deployment/frontend-deployment -n retailsense --timeout=120s || true
kubectl get pods -n retailsense

echo "Services:"
kubectl get svc -n retailsense

echo "Done."

# Notes:
# - Ensure your cluster has an nginx ingress controller if you plan to use the Ingress manifest.
# - For AWS EKS, build/push images to ECR and update image references in the manifests.
