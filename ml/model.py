import torch
import torch.nn as nn


class PricePredictor(nn.Module):
    def __init__(self, input_dim: int, hidden_dim1: int = 16, hidden_dim2: int = 8):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.ReLU(),
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.ReLU(),
            nn.Linear(hidden_dim2, 1),  # salida: target_pct_change_12m
        )

    def forward(self, x):
        # x: [batch, input_dim]
        return self.net(x).squeeze(-1)  # [batch]