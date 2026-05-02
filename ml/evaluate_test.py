import torch
import numpy as np
import pandas as pd
from pathlib import Path
from model import PricePredictor

BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data/processed"
MODEL_DIR = BASE_DIR / "models"

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

# Scale inputs
X_tensor = torch.from_numpy(X_test)
X_scaled = (X_tensor - X_mean) / X_std

# Predict
with torch.no_grad():
    preds = model(X_scaled).squeeze().numpy()

# Calculate values
idx_precio = feature_cols.index("precio")
precio_actual = X_test[:, idx_precio]

precio_futuro_real = precio_actual * (1 + y_test)
precio_futuro_pred = precio_actual * (1 + preds)

error_pct = np.abs(precio_futuro_pred - precio_futuro_real) / precio_futuro_real * 100

df = pd.DataFrame({
    "Precio Actual": precio_actual,
    "Var_Real": y_test * 100,
    "Var_Pred": preds * 100,
    "Precio Real 12m": precio_futuro_real,
    "Precio Pred 12m": precio_futuro_pred,
    "Error (%)": error_pct
})

print("=== RESUMEN GLOBAL DEL SET DE PRUEBAS (TEST) ===")
print(f"Total casos evaluados: {len(df)}")
print(f"Error Medio Absoluto (MAE) en predicción de precio: {error_pct.mean():.2f}%")
print(f"Error Mediano: {np.median(error_pct):.2f}%")
print("\n=== MUESTRA ALEATORIA DE 10 PREDICCIONES VS REALIDAD ===")
np.random.seed(42)
sample = df.sample(10).copy()

sample["Precio Actual"] = sample["Precio Actual"].map("{:.2f} €/m2".format)
sample["Var_Real"] = sample["Var_Real"].map("{:+.2f}%".format)
sample["Var_Pred"] = sample["Var_Pred"].map("{:+.2f}%".format)
sample["Precio Real 12m"] = sample["Precio Real 12m"].map("{:.2f} €/m2".format)
sample["Precio Pred 12m"] = sample["Precio Pred 12m"].map("{:.2f} €/m2".format)
sample["Error (%)"] = sample["Error (%)"].map("{:.2f}%".format)

print(sample.to_markdown(index=False))
