import os
from pathlib import Path
from typing import Dict, Any
import joblib
import json
from dotenv import load_dotenv


def load_models(model_path: str = None) -> Dict[str, Any]:
    load_dotenv()
    base = model_path or os.getenv("MODEL_PATH") or str(Path(__file__).resolve().parents[1] / "models")
    base_path = Path(base)
    models = {}

    def safe_load(p: Path):
        try:
            return joblib.load(p)
        except Exception:
            try:
                with open(p, "rb") as f:
                    return f.read()
            except Exception:
                return None

    candidates = {
        "lgbm": base_path / "lgbm_model.pkl",
        "xgboost": base_path / "xgboost_model.pkl",
        "scaler": base_path / "scaler.pkl",
        "kmeans": base_path / "kmeans_model.pkl",
        "gmm": base_path / "gmm_model.pkl",
        "le_family": base_path / "le_family.pkl",
        "le_type": base_path / "le_type.pkl",
        "features": base_path / "features.json",
    }

    for k, p in candidates.items():
        if p.exists():
            if p.suffix == ".json":
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        models[k] = json.load(f)
                except Exception:
                    models[k] = None
            else:
                models[k] = safe_load(p)
        else:
            models[k] = None

    # optionally load a training sample for drift comparisons
    training_sample = base_path / "training_sample.csv"
    if not training_sample.exists():
        alt = Path(__file__).resolve().parents[2] / "data" / "train.csv"
        training_sample = alt if alt.exists() else None

    models["training_sample_path"] = str(training_sample) if training_sample is not None else None

    return models
