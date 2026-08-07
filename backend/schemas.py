from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    app_name: str = Field(..., description="Application name")
    models_loaded: List[str] = Field(default_factory=list)


class ModelMetrics(BaseModel):
    rmse: float
    mae: float
    mape: float


class MetricsResponse(BaseModel):
    xgboost: ModelMetrics
    lightgbm: ModelMetrics
    arima: ModelMetrics


class ForecastRequest(BaseModel):
    store_nbr: int
    family: str
    onpromotion: int
    year: int
    month: int
    day: int
    dayofweek: int
    weekofyear: int
    quarter: int
    is_weekend: int
    is_holiday: int
    lag_7: float
    lag_14: float
    lag_28: float
    rolling_7_mean: float
    rolling_14_mean: float
    rolling_7_std: float
    dcoilwtico: float
    transactions: float
    cluster: int


class ForecastResponse(BaseModel):
    prediction: float
    model_used: str
    ci_lower: float
    ci_upper: float


class SegmentRequest(BaseModel):
    total_sales: float
    avg_sales: float
    std_sales: float
    total_promo: float
    avg_oil: float
    avg_trans: float
    holiday_count: float
    unique_families: float


class SegmentResponse(BaseModel):
    kmeans_cluster: int
    gmm_cluster: int
    gmm_confidence: float


class ExplainResponse(BaseModel):
    store_nbr: int
    feature_importance: Dict[str, float]


class ABTestRequest(BaseModel):
    features: List[Dict]
    true_values: List[float]


class ABTestResponse(BaseModel):
    xgb_mae: float
    lgb_mae: float
    t_stat: float
    p_value: float
    winner: str
    conclusion: str


class DriftResponse(BaseModel):
    drift_detected: bool
    drift_score: float
    affected_features: List[str]

