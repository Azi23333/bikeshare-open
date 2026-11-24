"""Compare HGB count and ratio targets on H1 2012 validation data.

Run from the repository root with python -m experiments.target_ratio_validation.
"""

import json

import numpy as np
from sklearn import __version__ as sklearn_version
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, r2_score

from src.config import ROOT, TARGET, VALID_END
from src.features import build_features, feature_columns
from src.ingest import load_raw
from src.train import MODELS, temporal_split

SCALE = "cnt_roll_7"
OUTPUT = ROOT / "reports" / "exercise4_validation.json"


def score(actual, predicted):
    return {
        "r2": round(float(r2_score(actual, predicted)), 4),
        "mae": round(float(mean_absolute_error(actual, predicted)), 1),
    }


def run() -> dict:
    raw = load_raw()
    features = build_features(raw[raw.dteday <= VALID_END])
    columns = feature_columns(features)
    train, valid, _ = temporal_split(features)
    train_scale, valid_scale = train[SCALE], valid[SCALE]
    for scale in (train_scale, valid_scale):
        if not (np.isfinite(scale) & scale.gt(0)).all():
            raise ValueError(f"{SCALE} must be finite and positive")

    x_train, x_valid = train[columns], valid[columns]
    y_train, y_valid = train[TARGET], valid[TARGET]
    scores = {}
    for name, estimator in MODELS.items():
        model = clone(estimator).fit(x_train, y_train)
        scores[name] = score(y_valid, model.predict(x_valid))

    train_ratio = y_train / train_scale
    ratio_model = clone(MODELS["hgb"]).fit(x_train, train_ratio)
    predicted_counts = ratio_model.predict(x_valid) * valid_scale.to_numpy()
    scores["hgb_ratio"] = score(y_valid, predicted_counts)

    return {
        "n_train": len(train),
        "n_valid": len(valid),
        "features": columns,
        "validation_end": VALID_END,
        "scikit_learn_version": sklearn_version,
        "target_transformation": f"{TARGET} / {SCALE}",
        "inverse_transformation": f"predicted_ratio * {SCALE}",
        "training_mean_count": round(float(y_train.mean()), 1),
        "validation_mean_count": round(float(y_valid.mean()), 1),
        "training_mean_ratio": round(float(train_ratio.mean()), 4),
        "validation_mean_ratio": round(float((y_valid / valid_scale).mean()), 4),
        "validation": scores,
        "hgb_ratio_minus_hgb": {
            "r2": round(scores["hgb_ratio"]["r2"] - scores["hgb"]["r2"], 4),
            "mae": round(scores["hgb_ratio"]["mae"] - scores["hgb"]["mae"], 1),
        },
    }


if __name__ == "__main__":
    result = json.dumps(run(), indent=2)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(result + "\n", encoding="utf-8")
    print(result)
