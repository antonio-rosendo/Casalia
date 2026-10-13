"""The MLP's network, kept from the first version; models.MLP trains it."""

import torch.nn as nn


class PricePredictor(nn.Module):
    def __init__(self, input_dim: int, hidden_dim1: int = 16, hidden_dim2: int = 8):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.ReLU(),
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.ReLU(),
            nn.Linear(hidden_dim2, 1),  # output: the 12-month change
        )

    def forward(self, x):
        # x: [batch, input_dim]
        return self.net(x).squeeze(-1)  # [batch]