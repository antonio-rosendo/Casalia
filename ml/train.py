import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
import torch.nn as nn
from pathlib import Path
from model import PricePredictor

DATA_DIR = Path("data/processed")
MODEL_DIR = Path("models")

def load_split(name):
    X = np.load(DATA_DIR / f"X_{name}.npy")
    y = np.load(DATA_DIR / f"y_{name}.npy")
    X_tensor = torch.from_numpy(X)
    y_tensor = torch.from_numpy(y)
    return X_tensor, y_tensor

def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    X_train, y_train = load_split("train")
    X_val, y_val     = load_split("val")

    input_dim = X_train.shape[1]
    model = PricePredictor(input_dim)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Normalización por media y desviación std de train
    X_mean = X_train.mean(dim=0, keepdim=True)
    X_std  = X_train.std(dim=0, keepdim=True) + 1e-8

    # Guardar stats para inferencia
    torch.save({"mean": X_mean, "std": X_std}, MODEL_DIR / "scaler.pt")

    X_train = (X_train - X_mean) / X_std
    X_val   = (X_val - X_mean) / X_std

    train_ds = TensorDataset(X_train, y_train)
    val_ds   = TensorDataset(X_val, y_val)

    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True)
    val_loader   = DataLoader(val_ds, batch_size=256, shuffle=False)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    num_epochs = 50

    for epoch in range(1, num_epochs + 1):
        # TRAIN
        model.train()
        train_loss = 0.0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)

            optimizer.zero_grad()
            preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * xb.size(0)

        train_loss /= len(train_ds)

        # VALIDACIÓN
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                preds = model(xb)
                loss = criterion(preds, yb)
                val_loss += loss.item() * xb.size(0)

        val_loss /= len(val_ds)

        print(f"Epoch {epoch}/{num_epochs} | train_loss={train_loss:.4f} | val_loss={val_loss:.4f}")

    # Guardar modelo entrenado
    torch.save(model.state_dict(), MODEL_DIR / "price_predictor.pt")

if __name__ == "__main__":
    main()