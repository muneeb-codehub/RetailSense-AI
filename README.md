# RetailSense AI

**Demand Forecasting & Customer Intelligence Platform**

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-326CE5)](https://kubernetes.io)
[![MLflow](https://img.shields.io/badge/MLflow-3.11-orange)](https://mlflow.org)
[![EC2](https://img.shields.io/badge/AWS-EC2-FF9900)](http://16.171.161.243:3000)

---

## Problem Statement

Retail chains operating across dozens of stores and hundreds of product families face a persistent forecasting problem: **demand is highly nonlinear**. Sales are shaped simultaneously by promotions, national holidays, oil prices (a proxy for economic conditions in Ecuador), store location, seasonal cycles, and historical lag patterns — none of which linear models handle well in combination.

Specifically, Corporación Favorita — one of Ecuador's largest grocery retailers — operates **54 stores** across multiple cities, carrying **33 product families**, with daily sales records spanning years. Their existing forecasting approach treated each store-family combination independently and relied on simple moving averages, producing errors too large to optimize inventory effectively. The consequences were real:

- **Overstocking** in slow periods locked up capital and increased waste
- **Understocking** during promotions and holidays caused lost sales and poor customer experience
- **No model visibility** — store managers could not understand why a forecast was high or low
- **No customer segmentation** — stores were treated as identical despite wildly different sales profiles
- **No model governance** — multiple model versions existed with no systematic comparison or tracking

---

## Solution: End-to-End ML Pipeline

RetailSense AI converts this problem into a **production-grade machine learning system** with full experiment tracking, model explainability, drift monitoring, and a live web dashboard.

### Pipeline Overview

```
Raw Data (CSV)
     │
     ▼
┌─────────────────────────────────┐
│  Feature Engineering            │
│  - Lag features (7, 14, 28 day) │
│  - Rolling statistics           │
│  - Date decomposition           │
│  - Holiday & oil encoding       │
│  - Store cluster assignment     │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Model Training (MLflow)        │
│  - XGBoost                      │
│  - LightGBM                     │
│  - ARIMA (baseline)             │
│  - K-Means / GMM segmentation   │
│  21 tracked runs, versioned     │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Model Selection (A/B Test)     │
│  Paired t-test on MAE           │
│  → LightGBM selected as best    │
│    (RMSE 336, MAE 229, MAPE 8%) │
│  → Registered as v3 in MLflow   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  FastAPI Backend                │
│  - /predict/forecast            │
│  - /predict/segment             │
│  - /explain/{store}  (SHAP)     │
│  - /ab-test                     │
│  - /drift                       │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  React Dashboard                │
│  Dashboard / Forecast /         │
│  Segmentation / Explainability  │
│  A/B Test / Drift               │
└─────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
  Docker Compose     Kubernetes
  (AWS EC2)          (Minikube on EC2)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data & Features | Pandas, NumPy, SQL window functions |
| ML Models | XGBoost, LightGBM, scikit-learn, statsmodels (ARIMA) |
| Clustering | K-Means, Gaussian Mixture Model (GMM) |
| Explainability | SHAP TreeExplainer |
| Experiment Tracking | MLflow 3.11 (21 tracked runs, model registry) |
| Backend API | FastAPI + Uvicorn |
| Frontend | React 18 + Recharts + TailwindCSS |
| Serving | Nginx (reverse proxy + static serving) |
| Storage | MinIO (S3-compatible), PostgreSQL |
| Containerization | Docker Compose |
| Orchestration | Kubernetes (Minikube on AWS EC2) |

---

## Model Results

| Model | RMSE | MAE | MAPE |
|-------|------|-----|------|
| **LightGBM** | **336.33** | **229.67** | **8.78%** |
| XGBoost | 360.22 | 245.97 | 9.46% |
| ARIMA (baseline) | 740.71 | 517.14 | 30.58% |

LightGBM selected as production model via paired t-test A/B comparison (p=0.0036, statistically significant).

**Top predictive features (SHAP):** `month`, `cluster`, `transactions`, `rolling_14_mean`, `family_enc`, `dayofweek`, `onpromotion`

---

## Screenshots

### Live Dashboard — EC2
![Live EC2 Dashboard](data/Screenshot%202026-04-30%20050222.jpg)

### Dashboard — Model Comparison
![Dashboard](data/Screenshot%202026-04-29%20044820.jpg)

> E2E health check confirms all models loaded and metrics accessible

![E2E Check](data/Screenshot%202026-04-29%20044847.jpg)

### Forecast — Input Form
![Forecast Input](data/Screenshot%202026-04-29%20044945.jpg)

### Forecast — Prediction Result
![Forecast Result](data/Screenshot%202026-04-29%20045007.jpg)

> Prediction: **2486 units** with 95% confidence interval [1827, 3146] using LightGBM

### Explainability — SHAP Feature Importance
![SHAP Explainability](data/Screenshot%202026-04-29%20045026.jpg)

### A/B Test — Model Comparison
![AB Test](data/Screenshot%202026-04-29%20045042.jpg)

> T-stat: -3.32 · P-value: 0.0036 · Winner: XGBoost (on this sample)

### MLflow — Experiment Home
![MLflow Home](data/Screenshot%202026-04-29%20221516.jpg)

### MLflow — 21 Training Runs
![MLflow Runs List](data/Screenshot%202026-04-29%20221545.jpg)

### MLflow — RMSE Comparison Across Runs
![MLflow RMSE Chart](data/Screenshot%202026-04-29%20035532.jpg)

> Best_Model_Production (LightGBM) at RMSE 336.33 vs ARIMA at 740.72

### MLflow — MAE & MAPE Comparison
![MLflow MAE Chart](data/Screenshot%202026-04-29%20221646.jpg)

### MLflow — ARIMA Run Detail
![MLflow ARIMA Run](data/Screenshot%202026-04-29%20221602.jpg)

> ARIMA(5,1,0): RMSE 740.71, MAE 517.14, MAPE 30.58% — confirms tree models vastly outperform the baseline

### MLflow — Best Model Registry
![MLflow Best Model](data/Screenshot%202026-04-29%20035455.jpg)

---

## Project Structure

```
retailsense-ai/
├── backend/
│   ├── main.py            # FastAPI app, lifespan, CORS
│   ├── predict.py         # Forecast, segment, explain, A/B, drift endpoints
│   ├── model_loader.py    # Loads .pkl models from /app/models
│   ├── drift_monitor.py   # KS-test drift detection
│   ├── schemas.py         # Pydantic request/response models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/         # Dashboard, Forecast, Segmentation, Explainability, ABTest, Drift
│   │   ├── components/    # Navbar, Sidebar, StatCard
│   │   └── api/api.js     # Axios client (baseURL: /api)
│   ├── nginx/default.conf # Proxies /api → backend:8000, /mlflow → mlflow:5000
│   └── Dockerfile
├── kubernetes/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── frontend-nginx-configmap.yaml  # Overrides nginx upstream for K8s service names
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml          # NodePort 30300
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml           # NodePort 30800
│   ├── mlflow-deployment.yaml
│   ├── mlflow-service.yaml            # NodePort 30500
│   └── ingress.yaml
├── models/                # Trained .pkl files (gitignored — transfer via scp)
│   ├── lgbm_model.pkl
│   ├── xgboost_model.pkl
│   ├── kmeans_model.pkl
│   ├── gmm_model.pkl
│   ├── scaler.pkl
│   ├── le_family.pkl
│   ├── le_type.pkl
│   └── features.json
├── notebooks/             # Training notebook + MLflow runs
├── data/                  # Raw CSVs (train, stores, oil, holidays)
├── scripts/               # Data loading + SQL feature engineering
├── mlflow/                # MLflow Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Local Development

```bash
# 1. Clone
git clone https://github.com/alyrraza/retailsense-ai.git
cd retailsense-ai

# 2. Copy env
cp .env.example .env

# 3. Copy model files (not in git)
# Place your .pkl files in ./models/

# 4. Run all services
docker compose up -d --build

# 5. Access
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000/docs
# MLflow:    http://localhost:5000
# MinIO:     http://localhost:9000
```

---

## EC2 Deployment (Docker Compose)

```bash
# On your local machine — copy models
scp -i "your-key.pem" -r ./models ubuntu@<EC2-IP>:~/retailsense-ai/

# On EC2
cd ~/retailsense-ai
cp .env.example .env
docker compose up -d --build

# Verify
docker compose ps
curl http://localhost:8000/
```

**Required EC2 Security Group inbound ports:** 22, 3000, 8000, 5001

---

## Kubernetes Deployment (Minikube on EC2)

```bash
# Prerequisites: Docker, Minikube, kubectl installed on EC2

# 1. Start Minikube with Docker driver
minikube start --driver=docker --memory=4096 --cpus=2

# 2. Build images inside Minikube's Docker context
eval $(minikube docker-env)
docker build -t retailsense-ai-backend:latest ./backend
docker build -t retailsense-ai-frontend:latest ./frontend

# 3. Apply all manifests
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/frontend-nginx-configmap.yaml
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/backend-service.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/frontend-service.yaml
kubectl apply -f kubernetes/mlflow-deployment.yaml
kubectl apply -f kubernetes/mlflow-service.yaml

# 4. Watch pods come up
kubectl get pods -n retailsense -w

# 5. Expose NodePorts on the EC2 host (Minikube Docker driver doesn't bind to host)
kubectl port-forward -n retailsense service/frontend-service 30300:80 --address 0.0.0.0 &
kubectl port-forward -n retailsense service/backend-service 30800:8000 --address 0.0.0.0 &
kubectl port-forward -n retailsense service/mlflow-service 30500:5000 --address 0.0.0.0 &
```

**Required EC2 Security Group inbound ports:** 22, 30300, 30800, 30500

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + loaded models |
| GET | `/metrics` | RMSE/MAE/MAPE for all models |
| POST | `/predict/forecast` | Sales forecast with CI |
| POST | `/predict/segment` | Store cluster (K-Means + GMM) |
| GET | `/explain/{store_nbr}` | SHAP feature importances |
| POST | `/ab-test` | Paired t-test: LightGBM vs XGBoost |
| GET | `/drift` | KS-test drift detection |

---

## Dataset

[Corporación Favorita Grocery Sales — Kaggle](https://www.kaggle.com/competitions/store-sales-time-series-forecasting)

- 54 stores · 33 product families · 4+ years of daily sales
- Supplementary: oil prices, national holidays, store metadata, transactions

## 📧 Contact

- **Email:** muneebarif226@gmail.com
- **GitHub:** [github.com/muneeb-codehub](https://github.com/muneeb-codehub)

## 📄 License

© 2025 Muneeb Arif. All rights reserved.

---

**Built with ❤️ by Muneeb Arif**
