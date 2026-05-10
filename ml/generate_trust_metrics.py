import json
import torch
import numpy as np
import pandas as pd
from pathlib import Path
from model import PricePredictor

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data/processed"
MODEL_DIR = BASE_DIR / "models"

def main():
    # Load test data and metadata
    X_test = np.load(DATA_DIR / "X_test.npy")
    y_test = np.load(DATA_DIR / "y_test.npy")
    meta_df = pd.read_csv(DATA_DIR / "meta_test.csv")

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

    # Scale inputs
    X_tensor = torch.from_numpy(X_test).float()
    X_scaled = (X_tensor - X_mean) / X_std

    # Predict
    with torch.no_grad():
        preds = model(X_scaled).squeeze().numpy()

    # Calculate errors
    idx_precio = feature_cols.index("precio")
    precio_actual = X_test[:, idx_precio]

    precio_futuro_real = precio_actual * (1 + y_test)
    precio_futuro_pred = precio_actual * (1 + preds)

    # Absolute percentage error
    error_pct = np.abs(precio_futuro_pred - precio_futuro_real) / precio_futuro_real * 100

    meta_df["error_pct"] = error_pct

    # Aggregate by comunidad
    error_by_comunidad = meta_df.groupby("comunidad")["error_pct"].mean().reset_index()
    
    confidence_data = {}
    print("=== TASA DE ERROR Y CONFIANZA POR COMUNIDAD ===")
    print(f"{'Comunidad':<25} | {'Error MAE (%)':<15} |  {'Categoría'}")
    print("-" * 65)

    for _, row in error_by_comunidad.iterrows():
        comunidad = row["comunidad"]
        mae = row["error_pct"]
        
        # Logic for categories (example bounds, can be tweaked)
        if mae < 3.0:
            category = "excellent"
        elif mae < 6.0:
            category = "good"
        elif mae < 10.0:
            category = "moderate"
        else:
            category = "low"
            
        confidence_data[comunidad] = {
            "mae_pct": round(float(mae), 2),
            "category": category
        }
        
        print(f"{comunidad:<25} | {mae:<15.2f} |  {category.upper()}")

    # Add a fallback 'nacional' or mean
    mean_mae = error_by_comunidad["error_pct"].mean()
    if mean_mae < 3.0:
        global_cat = "excellent"
    elif mean_mae < 6.0:
        global_cat = "good"
    elif mean_mae < 10.0:
        global_cat = "moderate"
    else:
        global_cat = "low"
        
    confidence_data["nacional"] = {
        "mae_pct": round(float(mean_mae), 2),
        "category": global_cat
    }
    
    print("-" * 65)
    print(f"{'nacional (media)':<25} | {mean_mae:<15.2f} |  {global_cat.upper()}")

    # Save to JSON
    out_path = DATA_DIR / "model_confidence.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(confidence_data, f, indent=4)
    print(f"\nGenerado archivo de confianza: {out_path}")

if __name__ == "__main__":
    main()
