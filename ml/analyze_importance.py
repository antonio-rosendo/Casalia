import torch
import numpy as np
import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data/processed"
MODEL_DIR = BASE_DIR / "models"

sys.path.append(str(BASE_DIR))
from model import PricePredictor

# Load test data
X_test = np.load(DATA_DIR / "X_test.npy")
y_test = np.load(DATA_DIR / "y_test.npy")

# Load scaler
scaler = torch.load(MODEL_DIR / "scaler.pt", map_location="cpu")
X_mean, X_std = scaler["mean"], scaler["std"]

# Load feature names
with open(DATA_DIR / "features.txt", encoding="utf-8") as f:
    feature_cols = [line.strip() for line in f if line.strip()]

input_dim = len(feature_cols)

# Load model
model = PricePredictor(input_dim=input_dim, hidden_dim1=32, hidden_dim2=16)
model.load_state_dict(torch.load(MODEL_DIR / "price_predictor.pt", map_location="cpu"))
model.eval()

# Baseline error
X_tensor = torch.from_numpy(X_test)
X_scaled = (X_tensor - X_mean) / X_std
with torch.no_grad():
    base_preds = model(X_scaled).squeeze().numpy()
base_error = np.mean(np.abs(base_preds - y_test))

importances = {}
for i, feature in enumerate(feature_cols):
    errors = []
    for _ in range(5):
        X_permuted = X_scaled.clone()
        # Permute the i-th column
        perm = torch.randperm(X_permuted.size(0))
        X_permuted[:, i] = X_permuted[perm, i]
        with torch.no_grad():
            preds = model(X_permuted).squeeze().numpy()
        errors.append(np.mean(np.abs(preds - y_test)))
    
    importances[feature] = np.mean(errors) - base_error

# Normalize to percentages relative to max feature
max_imp = max(max(importances.values()), 1e-9)
normalized = {k: max(0, (v / max_imp) * 100) for k, v in importances.items()}

print("Feature Importances:")
for k, v in normalized.items():
    print(f"{k}: {v:.2f}%")

# Group into the 5 categories
groups = {
    "priceDynamics": ["precio_lag_12m", "delta_precio_12m"],
    "macro": ["IPC", "IPC_lag_12m", "delta_IPC_12m", "num_hipotecas", "num_hipotecas_lag_12m", "delta_num_hipotecas_12m"],
    "currentPrice": ["precio"],
    "demographics": ["edad_media", "num_inmigracion"],
    "regional": ["year_t0", "month_t0"] # temporal
}

group_importances = {}
for group_name, feats in groups.items():
    val = sum(normalized.get(f, 0) for f in feats)
    group_importances[group_name] = val

# Re-normalize groups so the top one is roughly what it was before (or 100%)
# Or we can just sum the raw importances and normalize at the group level
raw_group = {g: sum(max(0, importances.get(f, 0)) for f in feats) for g, feats in groups.items()}
max_raw = max(max(raw_group.values()), 1e-9)

print("\nGroup Importances (Scaled 0-100):")
final_groups = {k: int((v / max_raw) * 100) for k, v in raw_group.items()}
print(final_groups)
