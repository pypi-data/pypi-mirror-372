import joblib
import numpy as np
import pandas as pd
import logging
import traceback
import torch
import os
import shap
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import matplotlib.pyplot as plt
import mlflow
import mlflow.pytorch
from gfa_ml.lib.default import (
    EPOCHS,
    BATCH_SIZE,
    PATIENCE,
    TRAIN_RATE,
    VALIDATION_RATE,
    TEST_RATE,
    HIDDEN_NEURONS,
    ACTIVATION_FUNCTION,
    DROP_RATE,
    OPTIMIZER,
    LOSS,
    LEARNING_RATE,
    HISTORY_SIZE,
    SMOOTH_WINDOW_SIZE,
    SAMPLE_SIZE,
    DEFAULT_RETENTION_PADDING,
    D_MODEL,
    NHEAD,
    NUM_LAYERS,
    DIM_FEEDFORWARD,
    DEFAULT_EXTENSION,
)
from gfa_ml.lib.constant import COLOR_MAP
from tqdm import tqdm
from gfa_ml.data_model.data_type import ModelType

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
from sklearn.metrics import mean_squared_error, r2_score
from gfa_ml.data_model.ml_model import (
    LSTMModel,
    MAPELoss,
    SMAPELoss,
    TransformerModel,
    MLModelWithScaler,
)
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


def moving_average(arr, window_size=10):
    try:
        # Pad start of array to keep same length
        cumsum = np.cumsum(np.insert(arr, 0, 0, axis=0), axis=0)
        ma = (cumsum[window_size:] - cumsum[:-window_size]) / window_size
        return ma
    except Exception as e:
        logging.error(f"Error calculating moving average: {e}")
        logging.error(traceback.format_exc())
        return None


def downsample(arr, num_points=200):
    try:
        # Downsample array along axis=0 to num_points points by uniform sampling
        indices = np.linspace(0, arr.shape[0] - 1, num_points).astype(int)
        return arr[indices], indices
    except Exception as e:
        logging.error(f"Error downsampling array: {e}")
        logging.error(traceback.format_exc())
        logging.error(
            f"Input array shape: {arr.shape}, Number of points requested: {num_points}"
        )
        return None, None


def create_time_aware_sequences(
    df: pd.DataFrame,
    input_cols: list,
    output_col: str,
    history_size: int,
    index_col: str = None,
    retention_period: int = 10,
    retention_col: str = None,
    retention_padding: int = DEFAULT_RETENTION_PADDING,  # only apply for specific stage in stora enso
    column_extension: str = None,
):
    try:
        if column_extension is not None and (
            f"{output_col}_{column_extension}" in df.columns
        ):
            output_col = f"{output_col}_{column_extension}"
        internal_df = df.copy()
        if index_col:
            internal_df.set_index(index_col, inplace=True)
            internal_df.sort_values(by=index_col)

        # get index where the output column is not Nan
        valid_indices = internal_df[output_col].index[internal_df[output_col].notna()]

        # fill nan by interpolation
        for col_i in input_cols:
            if col_i != output_col:
                internal_df[col_i] = internal_df[col_i].interpolate(
                    method="linear", limit_direction="both"
                )
            else:
                # fill nan by forward fill
                internal_df[col_i] = internal_df[col_i].ffill()
                internal_df[col_i] = internal_df[col_i].bfill()

        X = []
        y = []
        min_index = internal_df.index.min()
        max_index = internal_df.index.max()
        # iterate index in valid_indices
        for index_i in valid_indices:
            output_value = internal_df.loc[index_i][output_col]
            if pd.isna(output_value):
                continue
            if retention_col in internal_df.columns:
                retention_time = (
                    internal_df.loc[index_i][retention_col] + retention_padding
                )
            else:
                retention_time = retention_period
                print(f"Using default retention time: {retention_time}")

            start_index = index_i - (retention_time + history_size / 2)
            end_index = index_i - (retention_time - history_size / 2 + 1)

            if start_index < min_index or end_index >= max_index:
                continue

            input_sequence = internal_df.loc[int(start_index) : int(end_index)][
                input_cols
            ].values
            if input_sequence.shape[0] == history_size:
                X.append(input_sequence)
                y.append(output_value)
        return np.array(X), np.array(y)
    except Exception as e:
        logging.error(f"Error creating time-aware sequences: {e}")
        logging.error(traceback.format_exc())
        return None, None


def apply_scalers(X, y, x_scalers, y_scaler):
    X_norm = np.empty_like(X)
    for index, scaler in x_scalers.items():
        i = int(index)
        X_norm[:, :, i] = scaler.transform(X[:, :, i])
    y_norm = y_scaler.transform(y.reshape(-1, 1))

    return X_norm, y_norm


def normalize_sequences(X, y):
    try:
        n_features = X.shape[2]
        scalers = {}
        for i in range(n_features):
            scaler = MinMaxScaler()
            X[:, :, i] = scaler.fit_transform(X[:, :, i])
            scalers[i] = scaler

        y_scaler = MinMaxScaler()
        y = y_scaler.fit_transform(y.reshape(-1, 1)).flatten()
        logging.info("Sequences normalized successfully.")
        return X, y, scalers, y_scaler
    except Exception as e:
        logging.error(f"Error normalizing sequences: {e}")
        logging.error(traceback.format_exc())
        return X, y, {}, None


def split_time_series_data(
    X, y, train_ratio=TRAIN_RATE, validation_ratio=VALIDATION_RATE
):
    try:
        new_train_ratio = train_ratio / (train_ratio + validation_ratio)
        new_validation_ratio = validation_ratio / (train_ratio + validation_ratio)
        n = len(X)
        n_train = int(n * new_train_ratio)
        n_val = int(n * new_validation_ratio)

        X_train = X[:n_train]
        y_train = y[:n_train]

        X_val = X[n_train : n_train + n_val]
        y_val = y[n_train : n_train + n_val]

        logging.info(
            "Time series data split into train, validation, and test sets successfully."
        )
        return X_train, y_train, X_val, y_val
    except Exception as e:
        logging.error(f"Error splitting time series data: {e}")
        logging.error(traceback.format_exc())
        return None, None, None, None


def build_lstm_model(input_size: int, ml_model_config: dict):
    try:
        hidden_neurons: int = ml_model_config.get("hidden_neurons", HIDDEN_NEURONS)
        activation_function: str = ml_model_config.get(
            "activation_function", ACTIVATION_FUNCTION
        )
        drop_rate: float = ml_model_config.get("drop_rate", DROP_RATE)
        optimizer: str = ml_model_config.get("optimizer", OPTIMIZER)
        loss: str = ml_model_config.get("loss", LOSS)
        learning_rate: float = ml_model_config.get("learning_rate", LEARNING_RATE)
        num_layers: int = ml_model_config.get("num_layers", NUM_LAYERS)

        if activation_function.lower() == "tanh":
            activation_function = nn.Tanh
        elif activation_function.lower() == "relu":
            activation_function = nn.ReLU
        elif activation_function.lower() == "sigmoid":
            activation_function = nn.Sigmoid
        elif activation_function.lower() == "leakyrelu":
            activation_function = nn.LeakyReLU
        elif activation_function.lower() == "elu":
            activation_function = nn.ELU
        elif activation_function.lower() == "softmax":
            activation_function = nn.Softmax
        else:
            raise ValueError(f"Unsupported activation function: {activation_function}")
        model = LSTMModel(
            input_size=input_size,
            hidden_neurons=hidden_neurons,
            drop_rate=drop_rate,
            activation_function=activation_function,
            num_layers=num_layers,
        )
        logging.info("LSTM model built successfully.")

        # Setup optimizer
        if optimizer.lower() == "adam":
            optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer}")

        # Loss function
        if loss.lower() == "mse":
            loss_fn = nn.MSELoss()
        elif loss.lower() == "map":
            loss_fn = MAPELoss()
        elif loss.lower() == "smape":
            loss_fn = SMAPELoss()
        else:
            raise ValueError(f"Unsupported loss function: {loss}")

        return model, optimizer, loss_fn
    except Exception as e:
        logging.error(f"Error building LSTM model: {e}")
        logging.error(traceback.format_exc())
        return None


def build_transformer_model(input_size: int, ml_model_config: dict):
    try:
        d_model = ml_model_config.get("d_model", D_MODEL)
        nhead = ml_model_config.get("nhead", NHEAD)
        num_layers = ml_model_config.get("num_layers", NUM_LAYERS)
        dim_feedforward = ml_model_config.get("dim_feedforward", DIM_FEEDFORWARD)
        drop_rate = ml_model_config.get("drop_rate", DROP_RATE)
        activation_function = ml_model_config.get(
            "activation_function", ACTIVATION_FUNCTION
        )
        optimizer = ml_model_config.get("optimizer", OPTIMIZER)
        loss = ml_model_config.get("loss", LOSS)
        learning_rate = ml_model_config.get("learning_rate", LEARNING_RATE)

        if activation_function.lower() == "tanh":
            activation_fn = nn.Tanh
        elif activation_function.lower() == "relu":
            activation_fn = nn.ReLU
        elif activation_function.lower() == "sigmoid":
            activation_fn = nn.Sigmoid
        elif activation_function.lower() == "leakyrelu":
            activation_fn = nn.LeakyReLU
        elif activation_function.lower() == "elu":
            activation_fn = nn.ELU
        elif activation_function.lower() == "softmax":
            activation_fn = nn.Softmax
        else:
            raise ValueError(f"Unsupported activation function: {activation_function}")

        model = TransformerModel(
            input_size=input_size,
            d_model=d_model,
            nhead=nhead,
            num_layers=num_layers,
            dim_feedforward=dim_feedforward,
            drop_rate=drop_rate,
            activation_function=activation_fn,
        )
        logging.info("Transformer model built successfully.")

        if optimizer.lower() == "adam":
            optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer}")

        # Loss function
        if loss.lower() == "mse":
            loss_fn = nn.MSELoss()
        elif loss.lower() == "map":
            loss_fn = MAPELoss()
        elif loss.lower() == "smape":
            loss_fn = SMAPELoss()
        else:
            raise ValueError(f"Unsupported loss function: {loss}")

        return model, optimizer, loss_fn

    except Exception as e:
        logging.error(f"Error building Transformer model: {e}")
        logging.error(traceback.format_exc())
        return None


def train_and_evaluate(
    df: pd.DataFrame,
    ml_model_config: dict,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    patience: int = PATIENCE,
    plot: bool = False,
    explainability: bool = False,
    train_ratio: float = TRAIN_RATE,
    validation_ratio: float = VALIDATION_RATE,
    history_size: int = HISTORY_SIZE,
    input_cols: list = None,
    output_col: str = None,
    index_col: str = None,
    retention_col: str = None,
    smooth_window_size: int = SMOOTH_WINDOW_SIZE,
    sample_size: int = SAMPLE_SIZE,
    plot_path: str = None,
    run_name: str = None,
    mlflow_enable: bool = False,
    retention_padding: int = DEFAULT_RETENTION_PADDING,
    n_features_importance: int = None,
    use_markers: bool = False,
    model_path: str = None,
    interpolate_outliers: bool = False,
    image_extension: str = "svg",
    mlflow_run_id: str = None,
):
    try:
        if input_cols is None or output_col is None:
            logging.error("Input columns and output column must be specified.")
            return

        # split df in to train_validate df and test df
        test_ratio = 1 - train_ratio - validation_ratio
        # get the last part of the df following the test ratio for testing
        test_size = int(len(df) * test_ratio)
        test_df = df.iloc[-test_size:]
        train_validate_df = df.iloc[:-test_size]

        if interpolate_outliers:
            column_extension = DEFAULT_EXTENSION
        else:
            column_extension = None

        X, y = create_time_aware_sequences(
            train_validate_df,
            input_cols=input_cols,
            output_col=output_col,
            history_size=history_size,
            index_col=index_col,
            retention_col=retention_col,
            retention_padding=retention_padding,
            column_extension=DEFAULT_EXTENSION,
        )
        X_t, y_t = create_time_aware_sequences(
            test_df,
            input_cols=input_cols,
            output_col=output_col,
            history_size=history_size,
            index_col=index_col,
            retention_col=retention_col,
            retention_padding=retention_padding,
            column_extension=column_extension,
        )

        logging.info(f"Created dataset with X shape: {X.shape}, and y shape: {y.shape}")

        model_type = ml_model_config.get("model_type", ModelType.LSTM)
        if isinstance(model_type, str):
            model_type = ModelType(model_type.lower())

        ml_model_config["input_shape"] = X.shape

        if model_type == ModelType.LSTM:
            logging.info("Building LSTM model...")
            mlmodel, optimizer, loss_fn = build_lstm_model(
                input_size=X.shape[-1], ml_model_config=ml_model_config
            )
            logging.info("LSTM model built successfully.")
            if mlflow_enable:
                mlflow.log_param(
                    "hidden_neurons",
                    ml_model_config.get("hidden_neurons", HIDDEN_NEURONS),
                )
        elif model_type == ModelType.TRANSFORMER:
            mlmodel, optimizer, loss_fn = build_transformer_model(
                input_size=X.shape[-1], ml_model_config=ml_model_config
            )
            logging.info("Transformer model built successfully.")
            if mlflow_enable:
                mlflow.log_param("nhead", ml_model_config.get("nhead", NHEAD))
                mlflow.log_param("d_model", ml_model_config.get("d_model", D_MODEL))
                mlflow.log_param(
                    "dim_feedforward",
                    ml_model_config.get("dim_feedforward", DIM_FEEDFORWARD),
                )
        else:
            logging.error(f"Unsupported model type: {model_type}")

        X_norm, Y_norm, x_scalers, y_scaler = normalize_sequences(X, y)
        X_train, y_train, X_val, y_val = split_time_series_data(
            X_norm, Y_norm, train_ratio=train_ratio, validation_ratio=validation_ratio
        )

        joblib.dump({"input": x_scalers, "output": y_scaler}, "scalers.pkl")
        if mlflow_enable:
            mlflow.log_artifact("scalers.pkl", artifact_path="preprocessing")

        X_test, y_test = apply_scalers(X_t, y_t, x_scalers, y_scaler)

        logging.info(f"Data split into train, validation, and test sets.")

        # Set device for training
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {device}")
        mlmodel.to(device)

        # Convert numpy arrays to torch tensors and send to device
        X_train_t = torch.tensor(X_train, dtype=torch.float32)
        y_train_t = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)
        X_val_t = torch.tensor(X_val, dtype=torch.float32)
        y_val_t = torch.tensor(y_val, dtype=torch.float32).view(-1, 1)
        X_test_t = torch.tensor(X_test, dtype=torch.float32)
        y_test_t = torch.tensor(y_test, dtype=torch.float32).view(-1, 1)

        train_dataset = TensorDataset(X_train_t, y_train_t)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        val_dataset = TensorDataset(X_val_t, y_val_t)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        test_dataset = TensorDataset(X_test_t, y_test_t)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        logging.info("Data loaders created successfully.")

        # Training loop
        logging.info("Starting training loop...")
        train_loss_history = []
        val_loss_history = []
        loop = tqdm(range(epochs), desc="Training Model", unit="epoch")
        for epoch in loop:
            mlmodel.train()
            train_loss = 0.0

            for X_batch, y_batch in train_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)

                optimizer.zero_grad()
                outputs = mlmodel(X_batch)
                loss = loss_fn(outputs, y_batch)
                loss.backward()
                optimizer.step()
                train_loss += loss.item() * X_batch.size(0)

            # Average training loss
            train_loss /= len(train_loader.dataset)
            train_loss_history.append(train_loss)

            # Validation loss
            mlmodel.eval()
            with torch.no_grad():
                val_outputs = mlmodel(X_val_t.to(device))
                val_loss = loss_fn(val_outputs, y_val_t.to(device)).item()
                val_loss_history.append(val_loss)

            if (epoch + 1) % 20 == 0:  # Log every 20 epochs
                tqdm.write(
                    f"Epoch [{epoch + 1}/{epochs}], Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}"
                )
        if explainability:
            if device.type == "cpu":
                X_train_torch = torch.from_numpy(X_train).float()
                X_val_torch = torch.from_numpy(X_val).float()
            else:
                X_train_torch = torch.from_numpy(X_train).float().to(device)
                X_val_torch = torch.from_numpy(X_val).float().to(device)
            explainer = shap.GradientExplainer(mlmodel, X_train_torch)
            mlmodel.train()  # Ensure model is in training mode for SHAP
            shap_values = explainer.shap_values(X_val_torch)
            logging.info("SHAP values calculated successfully.")
            # Plot SHAP values
            shap_values = shap_values.squeeze(-1)
            # Get feature importance per sample
            feature_importance_per_sample = np.mean(np.abs(shap_values), axis=1)
            # Get time importance per sample
            time_importance_per_sample = np.mean(np.abs(shap_values), axis=2)

            # Plot feature importance
            smoothed_features = moving_average(
                feature_importance_per_sample, smooth_window_size
            )
            downsampled_features, downsampled_indices = downsample(
                arr=smoothed_features, num_points=sample_size
            )
            # sort downsampled in descending order by mean and rearrange order of the input_cols as following
            mean_importance = np.mean(downsampled_features, axis=0)
            sorted_indices = np.argsort(mean_importance)[::-1]
            downsampled_features = downsampled_features[:, sorted_indices]
            input_cols = [input_cols[i] for i in sorted_indices]

            plt.figure(figsize=(12, 6))
            # plot with different line styles
            line_count = 0
            for f in range(downsampled_features.shape[1]):
                if n_features_importance and line_count >= n_features_importance:
                    continue
                if use_markers:
                    color = COLOR_MAP[
                        list(COLOR_MAP.keys())[line_count % len(COLOR_MAP)]
                    ]
                    plt.plot(
                        downsampled_indices,
                        downsampled_features[:, f],
                        label=f"{input_cols[f]}",
                        color=color["color"],
                        linestyle=color["linestyle"],
                        marker=color["marker"],
                        linewidth=0.5,
                        markersize=3,
                    )
                else:
                    plt.plot(
                        downsampled_indices,
                        downsampled_features[:, f],
                        label=f"{input_cols[f]}",
                    )
                line_count += 1
            plt.xlabel("Sample Index")
            plt.ylabel("Mean |SHAP Value|")
            plt.title("Feature Importance Over Samples")
            plt.legend()
            if plot_path:
                if not os.path.exists(plot_path):
                    os.makedirs(plot_path)
                file_path = (
                    f"{plot_path}/{run_name}_feature_importance.{image_extension}"
                )
                plt.savefig(file_path, bbox_inches="tight")
                if mlflow_enable:
                    mlflow.log_artifact(file_path)
                logging.info(f"Plot saved to {file_path}")
            plt.show()

            # Plot time importance
            smoothed_time = moving_average(
                time_importance_per_sample, smooth_window_size
            )
            downsampled_time, downsampled_indices = downsample(
                arr=smoothed_time, num_points=sample_size
            )

            plt.figure(figsize=(12, 6))
            line_count = 0
            for t in range(downsampled_time.shape[1]):
                if use_markers:
                    color = COLOR_MAP[
                        list(COLOR_MAP.keys())[line_count % len(COLOR_MAP)]
                    ]
                    plt.plot(
                        downsampled_indices,
                        downsampled_time[:, t],
                        label=f"Time Step {t}",
                        color=color["color"],
                        linestyle=color["linestyle"],
                        marker=color["marker"],
                        linewidth=0.5,
                        markersize=3,
                    )
                else:
                    plt.plot(
                        downsampled_indices,
                        downsampled_time[:, t],
                        label=f"Time Step {t}",
                    )
                line_count += 1
            plt.xlabel("Sample Index")
            plt.ylabel("Mean |SHAP Value|")
            plt.title("Time Step Importance Over Samples")
            plt.legend()
            if plot_path:
                if not os.path.exists(plot_path):
                    os.makedirs(plot_path)
                file_path = (
                    f"{plot_path}/{run_name}_time_step_importance.{image_extension}"
                )
                plt.savefig(file_path, bbox_inches="tight")
                if mlflow_enable:
                    mlflow.log_artifact(file_path)
                logging.info(f"Plot saved to {file_path}")
            plt.show()
            logging.info("Explainability analysis completed successfully.")

        # Evaluate model
        mlmodel.eval()
        with torch.no_grad():
            test_outputs = mlmodel(X_test_t.to(device))
            test_loss = loss_fn(test_outputs, y_test_t.to(device)).item()
            test_outputs = test_outputs.cpu().numpy()
            y_test_t = y_test_t.cpu().numpy()
            y_test_t = y_test_t.reshape(-1, 1)
            test_outputs = y_scaler.inverse_transform(test_outputs)
            y_test_t = y_scaler.inverse_transform(y_test_t)
            # Calculate metrics
            test_mae = np.mean(np.abs(y_test_t - test_outputs))
            test_mse = np.mean(np.square(y_test_t - test_outputs))
            test_rmse = np.sqrt(test_mse)
            test_mape = np.mean(np.abs(y_test_t - test_outputs) / y_test_t) * 100

            if plot:
                plt.figure(figsize=(12, 6))
                plt.plot(y_test_t, label="True Values", color="blue")
                plt.plot(test_outputs, label="Predicted Values", color="red")
                plt.title("LSTM Model Predictions vs True Values")
                plt.xlabel("Time Steps")
                plt.ylabel("Brightness")
                plt.legend()
                if plot_path:
                    if not os.path.exists(plot_path):
                        os.makedirs(plot_path)
                    file_path = (
                        f"{plot_path}/{run_name}_test_prediction.{image_extension}"
                    )
                    plt.savefig(file_path, bbox_inches="tight")
                    if mlflow_enable:
                        mlflow.log_artifact(file_path)
                    logging.info(f"Plot saved to {file_path}")
                plt.show()

        # plot training and validation loss
        if plot:
            plt.figure(figsize=(12, 6))
            plt.plot(train_loss_history, label="Train Loss", color="blue")
            plt.plot(val_loss_history, label="Val Loss", color="red")
            plt.title("LSTM Model Training and Validation Loss")
            plt.xlabel("Epochs")
            plt.ylabel("Loss")
            plt.legend()
            if plot_path:
                if not os.path.exists(plot_path):
                    os.makedirs(plot_path)
                file_path = (
                    f"{plot_path}/{run_name}_train_validation_loss.{image_extension}"
                )
                plt.savefig(file_path, bbox_inches="tight")
                if mlflow_enable:
                    mlflow.log_artifact(file_path)
                logging.info(f"Plot saved to {file_path}")
            plt.show()
        input_example = np.array(X_test[:1], dtype=np.float32)
        raw_input_example = np.array(X_t[:1], dtype=np.float32)
        mlmodel = mlmodel.to("cpu")

        if mlflow_enable:
            mlflow.log_metric("test_loss", test_loss)
            mlflow.log_metric("test_mae", test_mae)
            mlflow.log_metric("test_mse", test_mse)
            mlflow.log_metric("test_rmse", test_rmse)
            mlflow.log_metric("test_mape", test_mape)
            if model_path and not os.path.exists(model_path):
                os.makedirs(model_path)
            try:
                model_info = mlflow.pytorch.log_model(
                    mlmodel, input_example=input_example, name=model_path
                )
                mlflow.pyfunc.log_model(
                    name="wrapped-model",
                    python_model=MLModelWithScaler(
                        model=mlmodel, scalers={"input": x_scalers, "output": y_scaler}
                    ),
                    artifacts={"model": model_info.model_uri, "scalers": "scalers.pkl"},
                    input_example=raw_input_example,
                )
            except Exception as e:
                logging.warning(f"Error logging model artifacts: {e}")
                model_info = mlflow.pytorch.log_model(
                    mlmodel, input_example=input_example, artifact_path=model_path
                )
                mlflow.pyfunc.log_model(
                    artifact_path="wrapped-model",
                    python_model=MLModelWithScaler(
                        model=mlmodel, scalers={"input": x_scalers, "output": y_scaler}
                    ),
                    artifacts={"model": model_info.model_uri, "scalers": "scalers.pkl"},
                    input_example=raw_input_example,
                )

        return {
            "train_loss": train_loss_history,
            "val_loss": val_loss_history,
            "test_loss": test_loss,
            "test_mae": test_mae,
            "test_mse": test_mse,
            "test_rmse": test_rmse,
            "test_mape": test_mape,
            "ml_model": mlmodel,
            "input_example": input_example,
        }

    except Exception as e:
        logging.error(f"Error during training and evaluation setup: {e}")
        logging.error(traceback.format_exc())
        return None


def mlflow_run(
    df: pd.DataFrame,
    parameter_dict: dict,
    experiment_name: str,
    run_name: str,
    explainability: bool = False,
    plot_path: str = None,
    model_path: str = None,
    azure_infrastructure: bool = False,
    interpolate_outliers: bool = False,
    image_extension: str = "svg",
):
    try:
        if azure_infrastructure:
            model_path = "models"

        data_config = parameter_dict.get("data_config", {})
        ml_model_config = parameter_dict.get("ml_model_config", {})
        training_config = parameter_dict.get("training_config", {})

        epochs = training_config.get("epochs", EPOCHS)
        batch_size = training_config.get("batch_size", BATCH_SIZE)
        patience = training_config.get("patience", PATIENCE)
        plot = training_config.get("plot", False)
        sample_size = training_config.get("sample_size", SAMPLE_SIZE)
        smooth_window_size = training_config.get(
            "smooth_window_size", SMOOTH_WINDOW_SIZE
        )
        n_features_importance = training_config.get("n_features_importance", None)
        use_markers = training_config.get("use_markers", False)

        activation_function = ml_model_config.get(
            "activation_function", ACTIVATION_FUNCTION
        )
        drop_rate = ml_model_config.get("drop_rate", DROP_RATE)
        optimizer = ml_model_config.get("optimizer", OPTIMIZER)
        loss = ml_model_config.get("loss", LOSS)
        learning_rate = ml_model_config.get("learning_rate", LEARNING_RATE)
        num_layers = ml_model_config.get("num_layers", 1)
        model_type = ml_model_config.get("model_type", "lstm")

        train_ratio = data_config.get("train_ratio", TRAIN_RATE)
        validation_ratio = data_config.get("validation_ratio", VALIDATION_RATE)
        history_size = data_config.get("history_size", HISTORY_SIZE)
        input_cols = data_config.get("input_cols", None)
        output_col = data_config.get("output_col", None)
        index_col = data_config.get("index_col", None)
        retention_col = data_config.get("retention_col", None)
        retention_padding = data_config.get("retention_padding", 0)

        mlflow.set_experiment(experiment_name)
        with mlflow.start_run(run_name=run_name, nested=True) as run:
            mlflow.log_param("epochs", epochs)
            mlflow.log_param("batch_size", batch_size)
            mlflow.log_param("patience", patience)
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("plot", plot)
            mlflow.log_param("sample_size", sample_size)
            mlflow.log_param("activation_function", activation_function)
            mlflow.log_param("drop_rate", drop_rate)
            mlflow.log_param("optimizer", optimizer)
            mlflow.log_param("loss", loss)
            mlflow.log_param("learning_rate", learning_rate)
            mlflow.log_param("num_layers", num_layers)
            mlflow.log_param("train_ratio", train_ratio)
            mlflow.log_param("validation_ratio", validation_ratio)
            mlflow.log_param("history_size", history_size)
            mlflow.log_param("output_col", output_col)
            mlflow.log_param("index_col", index_col)
            mlflow.log_param("retention_col", retention_col)
            mlflow.log_param("smooth_window_size", smooth_window_size)
            mlflow.log_param("explainability", explainability)
            mlflow.log_param("retention_padding", retention_padding)
            try:
                mlflow.log_param("input_cols", input_cols)
            except Exception as e:
                logging.error(f"Error logging input_cols: {e}")

            # train and evaluate ML models
            training_result = train_and_evaluate(
                df=df,
                ml_model_config=ml_model_config,
                epochs=epochs,
                batch_size=batch_size,
                patience=patience,
                plot=plot,
                explainability=explainability,
                train_ratio=train_ratio,
                validation_ratio=validation_ratio,
                history_size=history_size,
                input_cols=input_cols,
                output_col=output_col,
                index_col=index_col,
                retention_col=retention_col,
                plot_path=plot_path,
                run_name=run_name,
                mlflow_enable=True,
                retention_padding=retention_padding,
                n_features_importance=n_features_importance,
                use_markers=use_markers,
                sample_size=sample_size,
                smooth_window_size=smooth_window_size,
                model_path=model_path,
                interpolate_outliers=interpolate_outliers,
                image_extension=image_extension,
                mlflow_run_id=run.info.run_id,
            )

            # train_loss = training_result.get("train_loss", [])
            # val_loss = training_result.get("val_loss", [])
        test_loss = training_result.get("test_loss", -1)
        test_mae = training_result.get("test_mae", -1)
        test_mse = training_result.get("test_mse", -1)
        test_rmse = training_result.get("test_rmse", -1)
        test_mape = training_result.get("test_mape", -1)
        # ml_model = training_result.get("ml_model", None)
        # input_example = training_result.get("input_example", None)
        print(f"Test Loss: {test_loss:.6f}")
        print(f"Test MAE: {test_mae:.6f}")
        print(f"Test MSE: {test_mse:.6f}")
        print(f"Test RMSE: {test_rmse:.6f}")
        print(f"Test MAPE: {test_mape:.6f}%")

    except Exception as e:
        logging.error(f"Error during MLflow run setup: {e}")
        logging.error(traceback.format_exc())
        return None
