import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import pandas as pd

import model_loader
import drift_monitor
from schemas import HealthResponse, MetricsResponse, ModelMetrics
from predict import router as predict_router

load_dotenv()

LOGGER = logging.getLogger("retailsense_ai")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = os.getenv("MODEL_PATH") or str(Path(__file__).resolve().parents[1] / "models")
    LOGGER.info(f"Loading models from: {model_path}")
    models = model_loader.load_models(model_path)
    app.state.models = models
    yield
    # cleanup if needed


app = FastAPI(title="RetailSense AI - Backend", lifespan=lifespan)

# CORS for React frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    LOGGER.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception:
        LOGGER.exception("Request handling failed")
        raise
    LOGGER.info(f"Response status: {response.status_code} for {request.method} {request.url}")
    return response


@app.get("/", response_model=HealthResponse)
async def health():
    models = app.state.models or {}
    loaded = [k for k, v in models.items() if v is not None and k != "training_sample_path"]
    return HealthResponse(app_name="RetailSense AI", models_loaded=loaded)


@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    return MetricsResponse(
        xgboost=ModelMetrics(rmse=360.22, mae=245.97, mape=9.46),
        lightgbm=ModelMetrics(rmse=336.33, mae=229.67, mape=8.78),
        arima=ModelMetrics(rmse=740.71, mae=517.14, mape=30.58),
    )


@app.get("/drift")
async def drift(incoming_path: str = None):
    models = app.state.models or {}
    training_path = models.get("training_sample_path")
    if not training_path:
        raise HTTPException(status_code=500, detail="No training sample available for drift detection")

    if incoming_path:
        if not Path(incoming_path).exists():
            raise HTTPException(status_code=404, detail="incoming_path not found")
        incoming = pd.read_csv(incoming_path)
    else:
        try:
            incoming = pd.read_csv(training_path).sample(min(200, 1000))
        except Exception as e:
            LOGGER.exception("Failed loading training sample for drift")
            raise HTTPException(status_code=500, detail=f"Failed to load training sample: {e}")

    features = models.get("features") or []
    try:
        res = drift_monitor.detect_drift(training_path, incoming, features)
    except Exception as e:
        LOGGER.exception("Drift detection failed")
        raise HTTPException(status_code=500, detail=f"Drift detection error: {e}")

    return JSONResponse(content=res)


app.include_router(predict_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
