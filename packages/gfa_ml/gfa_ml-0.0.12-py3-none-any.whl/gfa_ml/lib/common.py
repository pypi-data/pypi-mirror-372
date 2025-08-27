import pandas as pd
import os
import importlib
import logging
import traceback
from typing import Dict, Union
import yaml
from ..data_model.common import Metric, MetricReport
from ..data_model.data_type import TimeUnit, TimeNormalizationType, ChartType
from .constant import DEFAULT_GRAPH_ATTRIBUTES, SRC_PATH, LIB_PATH, DOCS_PATH, IMG_PATH
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def convert_time_column(
    df: pd.DataFrame, time_column: str, unit: TimeUnit = TimeUnit.SECONDS.value
) -> pd.DataFrame:
    """
    Convert the time column of a DataFrame to datetime format.

    Args:
        df (pd.DataFrame): The DataFrame containing the time column (should be master data).
        time_column (str): The name of the time column to convert.
        unit (TimeUnit): The time unit to convert to.

    Returns:
        pd.DataFrame: The DataFrame with the converted and normalized time column.
    """
    if time_column not in df.columns:
        logging.error(f"Column '{time_column}' not found in DataFrame.")
        raise ValueError(f"Column '{time_column}' not found in DataFrame.")
    try:
        if unit.value == TimeUnit.SECONDS.value:
            div = 10**9
        elif unit.value == TimeUnit.MINUTES.value:
            div = 60 * 10**9
        elif unit.value == TimeUnit.HOURS.value:
            div = 60 * 60 * 10**9
        df[time_column] = pd.to_datetime(df[time_column]).astype(int) / div
        logging.info(f"Converted '{time_column}' to datetime with unit '{unit.value}'.")
    except Exception as e:
        logging.error(f"Error converting '{time_column}' to datetime: {e}")
        logging.warning("Returning unmodified DataFrame.")
        logging.info(traceback.format_exc())
    return df


def normalize_time_column(
    df: pd.DataFrame,
    time_column: str,
    unit: TimeUnit = TimeUnit.SECONDS,
    norm: TimeNormalizationType = TimeNormalizationType.ZERO_BASE_NORM,
) -> pd.DataFrame:
    """
    Normalize the time column of a DataFrame to a specified time unit.

    Args:
        df (pd.DataFrame): The DataFrame containing the time column (should be master data).
        time_column (str): The name of the time column to normalize.
        unit (TimeUnit): The time unit to normalize to.

    Returns:
        pd.DataFrame: The DataFrame with the normalized time column.
    """
    if time_column not in df.columns:
        raise ValueError(f"Column '{time_column}' not found in DataFrame.")
    try:
        df = convert_time_column(df, time_column, unit)
        if norm == TimeNormalizationType.ZERO_BASE_NORM:
            df[time_column] = df[time_column] - df[time_column].min()
            logging.info(f"Normalized '{time_column}' using zero normalization.")
        else:
            logging.warning(
                f"Normalization type '{norm.value}' not implemented. Returning unnormalized DataFrame."
            )
    except Exception as e:
        logging.error(f"Error normalizing '{time_column}': {e}")
        logging.warning("Returning unmodified DataFrame.")
        logging.debug(traceback.format_exc())
    return df


def gen_uml_diagram(
    class_object,
    format: str = "svg",
    output_file: str = None,
    graph_attributes: dict = None,
    docs: bool = False,
):
    """
    Generate a UML diagram for the given class object.
    class_object: The class object to generate the UML diagram.
    format: The format of the output file (default is "png").
    output_file: The name of the output file (default is "uml_diagram").
    graph_attributes: The attributes to apply to the graph (default is None).
    docs: If True, the output file will be saved in the docs/img directory.
    """
    try:
        erd = importlib.import_module("erdantic")
        if output_file is None:
            output_file = f"{class_object.__name__.lower()}_uml_diagram.{format}"
            if docs:
                output_file = os.path.join(IMG_PATH, output_file)
        diagram = erd.create(class_object)
        g = diagram.to_graphviz()
        if graph_attributes is None:
            graph_attributes = DEFAULT_GRAPH_ATTRIBUTES
        g.graph_attr.update(graph_attributes)
        g.layout(prog="dot")
        g.draw(f"{output_file}", format=format)
        logging.debug(f"UML diagram saved to {output_file}.")
    except Exception as e:
        logging.error(f"Error generating UML diagram: {e}")
        logging.debug(traceback.format_exc())


def load_metrics(file_path: str) -> Dict[str, Metric]:
    """
    Load metrics from a YAML file and return them as a dictionary.
    """
    try:
        with open(file_path) as file:
            metrics_data = yaml.safe_load(file)
        metrics = {}
        for metric_name, metric_info in metrics_data.items():
            metrics[metric_name] = Metric(**metric_info)
        return metrics
    except Exception as e:
        logging.error(f"Error loading metrics from {file_path}: {e}")
        logging.debug(traceback.format_exc())
        return {}


def load_multi_stage_metrics(file_path: str) -> Dict[str, Metric]:
    """
    Load metrics from a YAML file and return them as a dictionary.
    """
    try:
        with open(file_path) as file:
            metrics_data = yaml.safe_load(file)
        metrics = {}
        for stage, metric_dict in metrics_data.items():
            for metric_name, metric_info in metric_dict.items():
                metric_i = Metric.from_dict(metric_info)
                metrics[metric_name] = metric_i
                if metric_i.metric_name is None:
                    logging.warning(
                        f"Metric name is None for {metric_name} in stage {stage}."
                    )
        return metrics
    except Exception as e:
        logging.error(f"Error loading multi-stage metrics from {file_path}: {e}")
        logging.debug(traceback.format_exc())
        return {}


def plot_dataframe(
    dataframe: pd.DataFrame,
    title: str,
    x_col: Union[str, None],
    y_col: Union[str, list],
    xlabel: str,
    ylabel: str,
    plot_path: str = None,
    start_row: int = 0,
    end_row: int = -1,
    chart_type: ChartType = ChartType.LINE,
    fig_width: int = 10,
    fig_height: int = 6,
    save_plot: bool = False,
    remove_zeros: bool = True,
    remove_inf: bool = True,
    remove_negatives: bool = True,
    remove_nans: bool = True,
    start_percent: float = None,
    n_percent: float = None,
    n_rows: int = None,
    metrics: Union[Metric, Dict[str, Metric]] = None,
    include_tag: bool = False,
) -> None:
    """
    Plot a section of a DataFrame.

    Parameters:
    - dataframe: The DataFrame to plot.
    - title: The title of the plot.
    - x_col: The column to use for the x-axis.
    - y_col: The column(s) to use for the y-axis.
    - xlabel: The label for the x-axis.
    - ylabel: The label for the y-axis.
    - start_row: The starting row for the plot.
    - end_row: The ending row for the plot.
    - chart_type: The type of chart to plot (default is line chart).
    """
    try:
        if isinstance(y_col, str):
            list_y_col = [y_col]
        else:
            list_y_col = y_col
        if isinstance(metrics, Metric):
            metric_dict = {metrics.display_name: metrics}
        elif isinstance(metrics, dict):
            metric_dict = {m.display_name: m for m in metrics.values()}
        else:
            metric_dict = None

        # Validate start_row and end_row
        if start_row < 0 or start_row >= len(dataframe):
            start_row = 0
            logging.warning("start_row is less than 0, setting to 0.")
        if start_percent is not None:
            start_row = int(len(dataframe) * (start_percent / 100))
        if n_rows is not None:
            end_row = start_row + n_rows
        if n_percent is not None:
            end_row = start_row + int(len(dataframe) * (n_percent / 100))
        if end_row > len(dataframe):
            end_row = len(dataframe)
            logging.warning(
                "end_row is greater than DataFrame length, setting to DataFrame length."
            )
        if end_row < 0:
            end_row = len(dataframe) + end_row
            logging.warning("end_row is negative, setting to relative index.")
        logging.info(
            f"Plotting {end_row - start_row} rows from {start_row} to {end_row}., y_col: {list_y_col}"
        )

        plt.figure(figsize=(fig_width, fig_height))

        if xlabel is None:
            if x_col is None:
                xlabel = "Index"
            else:
                xlabel = x_col

        if title is None:
            title = f"Plot data over {x_col}"

        if save_plot:
            if plot_path is None:
                plot_path = f"{title.replace(' ', '_').lower()}"
            else:
                if not os.path.exists(plot_path):
                    os.makedirs(plot_path)
                plot_path = os.path.join(
                    plot_path, f"{title.replace(' ', '_').lower()}"
                )
        process_df = dataframe.iloc[start_row:end_row].copy()

        for col in list_y_col:
            if x_col is None:
                i_df = process_df[[col]].dropna()
                x_data = i_df.index.copy()
                y_data = i_df[col].copy()
            else:
                i_df = process_df[[x_col, col]].dropna()
                x_data = i_df[x_col].copy()
                y_data = i_df[col].copy()

            if metric_dict and col in metric_dict:
                metric_i = metric_dict[col]

            else:
                metric_i = None

            if include_tag and metric_i:
                label = f"{col}_{metric_i.tag}"
            else:
                label = col

            # new zip_df_data
            zip_df_data = pd.DataFrame({"x": x_data, "y": y_data})

            if remove_zeros:
                zip_df_data = zip_df_data[zip_df_data["y"] != 0]
            if remove_inf:
                zip_df_data = zip_df_data[
                    (zip_df_data["y"] != float("inf"))
                    & (zip_df_data["y"] != float("-inf"))
                ]
            if remove_negatives:
                zip_df_data = zip_df_data[zip_df_data["y"] >= 0]
            if remove_nans:
                zip_df_data = zip_df_data[~zip_df_data["y"].isna()]

            if chart_type == ChartType.LINE:
                plt.plot(zip_df_data["x"], zip_df_data["y"], label=label)
                plt.xlabel(xlabel)
                plt.legend()
                plt.grid()
                plt.title(title)
                plt.tight_layout()
                plot_path_i = f"{plot_path}_{start_row}_{end_row}_line.svg"
                if save_plot:
                    plt.savefig(plot_path_i, format="svg")
                    logging.info(f"Plot saved to {plot_path_i}.")
                plt.show()
            elif chart_type == ChartType.BAR:
                plt.bar(zip_df_data["x"], zip_df_data["y"], label=label)
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.legend()
                plt.title(title)
                plt.tight_layout()
                plot_path_i = f"{plot_path}_{start_row}_{end_row}_bar.svg"
                if save_plot:
                    plt.savefig(plot_path_i, format="svg")
                    logging.info(f"Plot saved to {plot_path_i}.")
                plt.show()
            elif chart_type == ChartType.HISTOGRAM:
                plt.hist(zip_df_data["y"], bins=100, label=label)
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.legend()
                plt.title(title)
                plt.tight_layout()
                plot_path_i = f"{plot_path}_{start_row}_{end_row}_histogram.svg"
                if save_plot:
                    plt.savefig(plot_path_i, format="svg")
                    logging.info(f"Plot saved to {plot_path_i}.")
                plt.show()
            # To do: Add other chart types like scatter, histogram, etc.
            else:
                logging.warning(f"Chart type {chart_type} not implemented.")
                continue
        if not save_plot:
            plt.close()
    except Exception as e:
        logging.error(f"Error plotting DataFrame: {e}")
        logging.info(traceback.format_exc())


def evaluate_metric_from_df(
    df: pd.DataFrame,
    metric_name: str,
    index_col: str = None,
    save_path: str = None,
    remove_zeros: bool = True,
    remove_inf: bool = True,
    remove_negatives: bool = True,
    remove_nans: bool = True,
    start_row: int = 0,
    end_row: int = -1,
    n_rows: int = None,
    n_percent: float = None,
    start_percent: float = None,
) -> MetricReport:
    """
    Evaluate a metric from a DataFrame and return a MetricReport.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        metric_name (str): The name of the metric to evaluate.
        index_col (str, optional): The column to use as the index. Defaults to None.

    Returns:
        MetricReport: The report containing the evaluation results.
    """
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
        logging.info(
            f"Evaluating metric '{metric_name}' from rows {start_row} to {end_row}."
        )
        process_df = df.iloc[start_row:end_row].copy()

        if index_col is not None:
            metric_df = process_df[[index_col, metric_name]].copy()
            metric_df.set_index(index_col, inplace=True)
        else:
            metric_df = process_df[[metric_name]].copy()

        col_series = (
            metric_df[metric_name] if metric_name in metric_df.columns else None
        )
        col_series = col_series.sort_index() if col_series is not None else None

        # Collecting statistics
        total_count = len(col_series) if col_series is not None else 0
        missing_count = col_series.isnull().sum() if col_series is not None else 0
        missing_rate = missing_count / total_count if total_count > 0 else 0
        zero_count = (col_series == 0).sum() if col_series is not None else 0
        zero_rate = zero_count / total_count if total_count > 0 else 0

        col_series = col_series.dropna() if col_series is not None else pd.Series()

        # remove zeros and inf values
        if remove_zeros:
            col_series = col_series[col_series != 0]
        if remove_inf:
            col_series = col_series[
                (col_series != float("inf")) & (col_series != float("-inf"))
            ]
        if remove_negatives:
            col_series = col_series[col_series >= 0]
        if remove_nans:
            col_series = col_series[~col_series.isna()]

        min_value = col_series.min() if col_series is not None else None
        max_value = col_series.max() if col_series is not None else None
        mean_value = col_series.mean() if col_series is not None else None
        value_range = (
            max_value - min_value
            if min_value is not None and max_value is not None
            else None
        )
        median_value = col_series.median() if col_series is not None else None
        standard_deviation = col_series.std() if col_series is not None else None
        variance = col_series.var() if col_series is not None else None
        quantile_25th = col_series.quantile(0.25) if col_series is not None else None
        quantile_75th = col_series.quantile(0.75) if col_series is not None else None
        interquartile_range = (
            quantile_75th - quantile_25th
            if quantile_25th is not None and quantile_75th is not None
            else None
        )
        skewness = col_series.skew() if col_series is not None else None
        kurtosis = col_series.kurt() if col_series is not None else None
        positive_count = (col_series > 0).sum() if col_series is not None else 0
        negative_count = (col_series < 0).sum() if col_series is not None else 0
        positive_rate = positive_count / total_count if total_count > 0 else 0
        negative_rate = negative_count / total_count if total_count > 0 else 0

        # Calculate time drift metrics
        non_nan_series = (
            col_series.dropna().sort_index() if col_series is not None else pd.Series()
        )
        time_drift = (
            non_nan_series.index.to_series().diff().dropna()
            if not non_nan_series.empty
            else pd.Series()
        )
        mean_measurement_interval = time_drift.mean() if not time_drift.empty else None
        max_measurement_interval = time_drift.max() if not time_drift.empty else None
        min_measurement_interval = time_drift.min() if not time_drift.empty else None

        report = MetricReport(
            metric_name=metric_name,
            total_count=total_count,
            missing_count=missing_count,
            missing_rate=missing_rate,
            zero_count=zero_count,
            zero_rate=zero_rate,
            min_value=min_value,
            max_value=max_value,
            value_range=value_range,
            mean_value=mean_value,
            median_value=median_value,
            standard_deviation=standard_deviation,
            variance=variance,
            quantile_25th=quantile_25th,
            quantile_75th=quantile_75th,
            interquartile_range=interquartile_range,
            skewness=skewness,
            kurtosis=kurtosis,
            positive_count=positive_count,
            negative_count=negative_count,
            positive_rate=positive_rate,
            negative_rate=negative_rate,
            mean_measurement_interval=mean_measurement_interval,
            max_measurement_interval=max_measurement_interval,
            min_measurement_interval=min_measurement_interval,
        )

        if save_path:
            report.save_to_yaml(
                os.path.join(save_path, f"{metric_name}_{start_row}_{end_row}.yaml")
            )
            logging.info(f"Metric report saved to {save_path}.")
        return report
    except Exception as e:
        logging.error(f"Error evaluating metric '{metric_name}': {e}")
        logging.info(traceback.format_exc())
        return MetricReport(metric_name=metric_name, value=None, error=str(e))


def map_data_columns(
    df: pd.DataFrame,
    metric_dict: Dict[str, Metric],
) -> pd.DataFrame:
    """
    Map the columns of a DataFrame based on a dictionary of metrics.

    Args:
        df (pd.DataFrame): The DataFrame to map.
        metric_dict (Dict[str, Metric]): A dictionary mapping metric names to Metric objects.

    Returns:
        pd.DataFrame: The DataFrame with mapped columns.
    """
    try:
        for metric_name, metric in metric_dict.items():
            # rename the columns in the DataFrame
            if metric.column_name not in df.columns:
                logging.warning(
                    f"Column {metric.column_name} not found in DataFrame while mapping."
                )
                continue
            df.rename(columns={metric.column_name: metric.display_name}, inplace=True)
    except Exception as e:
        logging.error(f"Error mapping data columns: {e}")
    return df
