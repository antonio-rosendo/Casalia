import torch
import numpy as np
from pathlib import Path
from model import PricePredictor

DATA_DIR = Path("data/processed")
MODEL_DIR = Path("models")


def load_scaler():
    scaler = torch.load(MODEL_DIR / "scaler.pt", map_location="cpu")
    return scaler["mean"], scaler["std"]


def load_model():
    # Leemos nombres de columnas de entrada
    with open(DATA_DIR / "features.txt", encoding="utf-8") as f:
        feature_cols = [line.strip() for line in f if line.strip()]
    input_dim = len(feature_cols)

    model = PricePredictor(input_dim=input_dim, hidden_dim1=32, hidden_dim2=16)
    state_dict = torch.load(MODEL_DIR / "price_predictor.pt", map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    return model, feature_cols


def predict_pct_change_12m(features_dict):
    """
    features_dict: diccionario con keys = nombres de feature_cols
    y values = valores numéricos para una comunidad y mes concretos.
    Devuelve la variación porcentual de precio estimada a 12 meses.
    """
    model, feature_cols = load_model()
    X_mean, X_std = load_scaler()

    x = np.array([[features_dict[col] for col in feature_cols]], dtype=np.float32)
    x_tensor = torch.from_numpy(x)
    x_tensor = (x_tensor - X_mean) / X_std

    with torch.no_grad():
        pred = model(x_tensor).item()  # por ejemplo 0.05 = +5 %

    return pred