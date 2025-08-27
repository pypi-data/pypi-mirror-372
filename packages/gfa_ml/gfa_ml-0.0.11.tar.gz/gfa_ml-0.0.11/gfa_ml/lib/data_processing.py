import pandas as pd
import os
import logging
import traceback
from typing import Dict, Union
import yaml
from ..data_model.common import Metric, MetricReport
from ..data_model.data_type import TimeUnit, TimeNormalizationType, ChartType
from .constant import DEFAULT_GRAPH_ATTRIBUTES, SRC_PATH, LIB_PATH, DOCS_PATH, IMG_PATH
import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def smooth_data_frame(
    df: pd.DataFrame, metric_dict: Dict[str, Metric], inplace: bool = True
) -> pd.DataFrame:
    """
    Apply smoothing to the DataFrame based on the metric definitions.
    """
    try:
        new_df = df.copy()
        for metric_name, metric in metric_dict.items():
            column_name = metric.display_name
            if inplace == False:
                new_col_name = f"{column_name}_interpolated"
                if new_col_name not in new_df.columns:
                    new_df[new_col_name] = new_df[column_name].copy()
                column_name = new_col_name
            if column_name not in new_df.columns:
                logging.warning(
                    f"Column '{column_name}' not found in DataFrame. Skipping smoothing for this metric."
                )
                continue
            if metric.smoothing_function:
                logging.info(
                    f"Smoothing column: {column_name} with {metric.smoothing_function.function_name}"
                )
                if metric.smoothing_function.function_name == "moving_average":
                    window_size = metric.smoothing_function.smoothing_param.window_size
                    min_periods = metric.smoothing_function.smoothing_param.min_periods
                    new_df[column_name] = (
                        new_df[column_name]
                        .rolling(window=window_size, min_periods=min_periods)
                        .mean()
                    )
        return new_df
    except Exception as e:
        logging.error(f"Error occurred while smoothing data frame: {e}")
        logging.error(traceback.format_exc())
        return df


def extract_dataframe(
    df: pd.DataFrame,
    remove_zeros: bool = False,
    remove_inf: bool = False,
    remove_negatives: bool = False,
    remove_nans: bool = False,
    start_row: int = 0,
    end_row: int = -1,
    n_rows: int = None,
    n_percent: float = None,
    start_percent: float = None,
) -> pd.DataFrame:
    try:
        if start_row < 0 or start_row >= len(df):
            start_row = 0
            logging.warning("start_row is less than 0, setting to 0.")
        if start_percent is not None:
            start_row = int(len(df) * (start_percent / 100))
        if n_rows is not None:
            end_row = start_row + n_rows
        if n_percent is not None:
            end_row = start_row + int(len(df) * (n_percent / 100))
        if end_row > len(df):
            end_row = len(df)
            logging.warning(
                "end_row is greater than DataFrame length, setting to DataFrame length."
            )
        if end_row < 0:
            end_row = len(df) + end_row
            logging.warning("end_row is negative, setting to relative index.")

        process_df = df.iloc[start_row:end_row].copy()
        if remove_zeros:
            process_df = process_df[(process_df != 0).all(axis=1)]
        if remove_inf:
            process_df = process_df[
                (process_df != float("inf")).all(axis=1)
                & (process_df != float("-inf")).all(axis=1)
            ]
        if remove_negatives:
            process_df = process_df[(process_df >= 0).all(axis=1)]
        if remove_nans:
            process_df = process_df.dropna()
        logging.info(
            f"Extracted DataFrame from rows {start_row} to {end_row} with shape {process_df.shape}."
        )
        return process_df
    except Exception as e:
        logging.error(f"Error extracting DataFrame: {e}")
        logging.debug(traceback.format_exc())
        return pd.DataFrame()


def remove_outliers_sliding_window(
    df, window=100, upper_threshold=0.9, lower_threshold=0.1, cols: list = None
):
    try:
        clean_df = df.copy()
        if cols is None:
            cols = df.select_dtypes(include="number").columns
        for col in cols:
            mask = np.ones(len(df), dtype=bool)  # keep track of valid rows
            for i in range(len(df)):
                start = max(0, i - window // 2)
                end = min(len(df), i + window // 2)
                window_data = df[col].iloc[start:end]

                Q1 = window_data.quantile(lower_threshold)
                Q3 = window_data.quantile(upper_threshold)

                if not (Q1 <= df[col].iloc[i] <= Q3):
                    mask[i] = False
            clean_df = clean_df[mask]
        return clean_df
    except Exception as e:
        logging.error(f"Error removing outliers (sliding window): {e}")
        logging.info(traceback.format_exc())
        return df


def remove_outliers_sliding_zscore(
    df: pd.DataFrame, window: int = 100, threshold: int = 3, cols: list = None
):
    try:
        clean_df = df.copy()
        if cols is None:
            cols = df.select_dtypes(include="number").columns
        for col in cols:
            rolling_mean = df[col].rolling(window, center=True, min_periods=1).mean()
            rolling_std = df[col].rolling(window, center=True, min_periods=1).std()
            z_scores = (df[col] - rolling_mean) / rolling_std
            mask = np.abs(z_scores) <= threshold
            clean_df = clean_df[mask]
        return clean_df
    except Exception as e:
        logging.error(f"Error removing outliers (sliding z-score): {e}")
        logging.info(traceback.format_exc())
        return df


def interpolate_outliers_sliding(
    df: pd.DataFrame,
    window: int = 100,
    threshold: int = 3,
    method: str = "zscore",
    cols: list = None,
    inplace: bool = True,
):
    clean_df = df.copy()

    if cols is None:
        cols = clean_df.columns

    for col in cols:
        if inplace == False:
            new_col_name = f"{col}_interpolated"
            clean_df[new_col_name] = clean_df[col].copy()
            col = new_col_name
        if method == "zscore":
            rolling_mean = (
                clean_df[col].rolling(window, center=True, min_periods=1).mean()
            )
            rolling_std = (
                clean_df[col].rolling(window, center=True, min_periods=1).std()
            )
            z_scores = (clean_df[col] - rolling_mean) / rolling_std
            outliers = np.abs(z_scores) > threshold

        elif method == "iqr":
            rolling_q1 = (
                clean_df[col].rolling(window, center=True, min_periods=1).quantile(0.25)
            )
            rolling_q3 = (
                clean_df[col].rolling(window, center=True, min_periods=1).quantile(0.75)
            )
            iqr = rolling_q3 - rolling_q1
            lower = rolling_q1 - 1.5 * iqr
            upper = rolling_q3 + 1.5 * iqr
            outliers = (clean_df[col] < lower) | (clean_df[col] > upper)

        clean_df.loc[outliers, col] = np.nan

        clean_df[col] = clean_df[col].interpolate(method="linear").ffill().bfill()

    return clean_df


def remove_interpolated_values(df: pd.DataFrame, cols: list = None) -> pd.DataFrame:
    if cols is None:
        cols = df.columns
    for col in cols:
        interpolated_col = f"{col}_interpolated"
        null_indices = df[col].isna()
        # set value to null in interpolated column where original column is null
        df[interpolated_col] = df[interpolated_col].mask(null_indices)
    return df
