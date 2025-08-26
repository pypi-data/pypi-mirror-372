import torch
import torch.nn as nn
import torch.optim as optim
import logging
import mlflow.pyfunc
import mlflow.pytorch
import joblib
import numpy as np
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def mape_loss(output, target, epsilon=1e-8):
    """
    Mean Absolute Percentage Error (MAPE) Loss
    output: predictions (batch_size, *)
    target: ground truth (batch_size, *)
    epsilon: to avoid division by zero
    """
    try:
        return torch.mean(torch.abs((target - output) / (target + epsilon))) * 100
    except Exception as e:
        logging.error(f"Error calculating MAPE loss: {e}")
        return None


class MAPELoss(nn.Module):
    def __init__(self, epsilon=1e-8):
        super().__init__()
        self.epsilon = epsilon

    def forward(self, output, target):
        return torch.mean(torch.abs((target - output) / (target + self.epsilon))) * 100


class SMAPELoss(nn.Module):
    def __init__(self, epsilon=1e-8):
        super().__init__()
        self.epsilon = epsilon

    def forward(self, y_pred, y_true):
        return (
            torch.mean(
                torch.abs(y_true - y_pred)
                / (torch.abs(y_true) + torch.abs(y_pred) + self.epsilon)
                * 2
            )
            * 100
        )


class LSTMModel(nn.Module):
    def __init__(
        self,
        input_size,
        hidden_neurons,
        drop_rate=0.0,
        output_size=1,
        activation_function=nn.Tanh,
        num_layers=1,
    ):
        super().__init__()
        self.hidden_neurons = hidden_neurons
        self.activation = activation_function()

        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_neurons,
            num_layers=num_layers,
            batch_first=True,
            dropout=drop_rate,
        )

        # Fully connected output layer
        self.fc = nn.Linear(hidden_neurons, output_size)

    def forward(self, x):
        # LSTM returns outputs for all time steps and the hidden/cell states
        lstm_out, (h_n, c_n) = self.lstm(x)
        last_hidden_state = h_n[-1]  # (batch_size, hidden_neurons)
        activated = self.activation(last_hidden_state)
        out = self.fc(activated)  # (batch_size, output_size)
        return out


class TransformerModel(nn.Module):
    def __init__(
        self,
        input_size,
        d_model=64,
        nhead=4,
        num_layers=2,
        dim_feedforward=128,
        drop_rate=0.1,
        activation_function=nn.ReLU,
    ):
        super().__init__()
        self.input_size = input_size
        self.d_model = d_model

        # Input projection
        self.input_proj = nn.Linear(input_size, d_model)

        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=drop_rate,
            activation=activation_function(),
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        # Output projection (1-step prediction)
        self.output_proj = nn.Linear(d_model, 1)

    def forward(self, x):
        """
        x: (batch_size, seq_len, input_size)
        """
        x = self.input_proj(x)  # (batch_size, seq_len, d_model)
        x = x.permute(1, 0, 2)  # Transformer expects (seq_len, batch_size, d_model)
        x = self.transformer_encoder(x)
        x = x.permute(1, 0, 2)  # Back to (batch_size, seq_len, d_model)
        x = self.output_proj(x[:, -1, :])  # Use last timestep for prediction
        return x


class MLModelWithScaler(mlflow.pyfunc.PythonModel):
    def __init__(self, model, scalers):
        self.model = model
        self.scalers = scalers

    @classmethod
    def load_model_from_dir(cls, model_dir):
        model = mlflow.pytorch.load_model(os.path.join(model_dir, "models"))
        model.eval()
        scalers = joblib.load(os.path.join(model_dir, "scalers.pkl"))
        return cls(model, scalers)

    def predict(self, X):
        # Scale the input
        X_norm = np.empty_like(X)
        for index, scaler in self.scalers["input"].items():
            i = int(index)
            X_norm[:, :, i] = scaler.transform(X[:, :, i])
        # Make predictions
        with torch.no_grad():
            X_tensor = torch.tensor(X_norm, dtype=torch.float32)
            y_norm = self.model(X_tensor).numpy()
        y_scaler = self.scalers["output"]
        y = y_scaler.inverse_transform(y_norm)
        return y
