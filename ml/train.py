import copy
import random

import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
import torch.nn as nn
from pathlib import Path
from model import PricePredictor

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data/processed"
MODEL_DIR = BASE_DIR / "models"

SEED = 42


def set_seed(seed: int = SEED):
    """Fija todas las fuentes de aleatoriedad para que el entrenamiento sea reproducible."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_split(name: str):
    X = np.load(DATA_DIR / f"X_{name}.npy")
    y = np.load(DATA_DIR / f"y_{name}.npy")
    X_tensor = torch.from_numpy(X)
    y_tensor = torch.from_numpy(y)
    return X_tensor, y_tensor


def main():
    set_seed()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    X_train, y_train = load_split("train")
    X_val, y_val = load_split("val")

    input_dim = X_train.shape[1]
    model = PricePredictor(input_dim=input_dim, hidden_dim1=32, hidden_dim2=16)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Normalización de inputs
    X_mean = X_train.mean(dim=0, keepdim=True)
    X_std = X_train.std(dim=0, keepdim=True) + 1e-8

    torch.save({"mean": X_mean, "std": X_std}, MODEL_DIR / "scaler.pt")

    X_train = (X_train - X_mean) / X_std
    X_val = (X_val - X_mean) / X_std

    train_ds = TensorDataset(X_train, y_train)
    val_ds = TensorDataset(X_val, y_val)

    train_loader = DataLoader(
        train_ds,
        batch_size=64,
        shuffle=True,
        generator=torch.Generator().manual_seed(SEED),
    )
    val_loader = DataLoader(val_ds, batch_size=128, shuffle=False)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(
        model.parameters(), lr=1e-3, weight_decay=1e-3
    )  # pequeño weight decay

    num_epochs = 80

    best_val_loss = float("inf")
    best_state_dict = None
    best_epoch = None

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

        # VALIDATION
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                preds = model(xb)
                loss = criterion(preds, yb)
                val_loss += loss.item() * xb.size(0)
        val_loss /= len(val_ds)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch
            # deepcopy: state_dict() devuelve los mismos tensores que el modelo sigue
            # modificando, así que sin copia se acabaría guardando la última época.
            best_state_dict = copy.deepcopy(model.state_dict())

        print(
            f"Epoch {epoch:03d}/{num_epochs} | "
            f"train_loss={train_loss:.6f} | val_loss={val_loss:.6f}"
        )

    # Guardamos el mejor modelo (por val_loss)
    if best_state_dict is not None:
        model.load_state_dict(best_state_dict)
        print(f"Best epoch: {best_epoch} | val_loss={best_val_loss:.6f}")
    torch.save(model.state_dict(), MODEL_DIR / "price_predictor.pt")


if __name__ == "__main__":
    main()