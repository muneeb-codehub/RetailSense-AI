from typing import List, Dict, Any
import pandas as pd
from scipy.stats import ks_2samp


def load_csv(path: str):
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def detect_drift(training_path: str, incoming_df: pd.DataFrame, features: List[str], alpha: float = 0.05) -> Dict[str, Any]:
    training_df = load_csv(training_path) if training_path else None
    if training_df is None:
        return {"drift_detected": False, "drift_score": 0.0, "affected_features": []}

    affected = []
    p_values = []

    for f in features:
        if f not in training_df.columns or f not in incoming_df.columns:
            continue
        try:
            stat, p = ks_2samp(training_df[f].dropna(), incoming_df[f].dropna())
            p_values.append(p)
            if p < alpha:
                affected.append(f)
        except Exception:
            continue

    drift_detected = len(affected) > 0
    # define a simple drift score: 1 - min(p) (higher -> more drift)
    drift_score = 1.0 - min(p_values) if p_values else 0.0

    return {"drift_detected": drift_detected, "drift_score": float(drift_score), "affected_features": affected}
"""Lightweight drift monitoring utilities (placeholder).
Replace with hooks to MLflow, Evidently, or custom logic.
"""


def check_drift(baseline_stats: dict, current_stats: dict) -> dict:
    """Compare baseline and current feature stats and report simple thresholds."""
    report = {"drift": False, "features": {}}
    for feat, base in baseline_stats.items():
        cur = current_stats.get(feat)
        if cur is None:
            continue
        # naive check: mean shift
        mean_shift = abs(cur.get("mean", 0) - base.get("mean", 0))
        drifted = mean_shift > (base.get("std", 1) * 3)
        report["features"][feat] = {"mean_shift": mean_shift, "drifted": drifted}
        if drifted:
            report["drift"] = True
    return report
