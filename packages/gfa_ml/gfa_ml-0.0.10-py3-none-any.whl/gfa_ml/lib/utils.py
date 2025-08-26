import os
from typing import Union
import logging
import traceback
import json
import pandas as pd
import yaml
from typing import Literal
import copy

from gfa_ml.data_model.common import RunConfig

# import seaborn as sns

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def save_yaml(
    dictionary: dict,
    path: str,
    sort_keys: bool = False,
    allow_unicode: bool = True,
    default_flow_style: bool = False,
):
    try:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "w") as file:
            yaml.dump(
                dictionary,
                file,
                default_flow_style=default_flow_style,
                sort_keys=sort_keys,
                allow_unicode=allow_unicode,
                Dumper=NoAliasDumper,
            )
    except Exception as e:
        logging.error(f"Error saving YAML file {path}: {e}")
        logging.debug(traceback.format_exc())


def load_yaml(path: str) -> dict:
    try:
        if not os.path.exists(path):
            logging.error(f"YAML file {path} does not exist.")
            return {}
        with open(path, "rb") as file:
            content = yaml.load(file, Loader=yaml.FullLoader)
        return content
    except Exception as e:
        logging.error(f"Error loading YAML file {path}: {e}")
        logging.debug(traceback.format_exc())
        return {}


def save_json(dictionary: dict, path: str):
    try:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "w") as file:
            json.dump(dictionary, file)
    except Exception as e:
        logging.error(f"Error saving JSON file {path}: {e}")
        logging.debug(traceback.format_exc())


def load_json(path: str) -> dict:
    try:
        with open(path, "rb") as file:
            content = json.load(file)
        return content
    except Exception as e:
        logging.error(f"Error loading JSON file {path}: {e}")
        logging.debug(traceback.format_exc())
        return {}


def load_csv_to_dataframe(file_path: str) -> Union[pd.DataFrame, None]:
    """
    Loads a CSV file into a Pandas DataFrame.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    pd.DataFrame: A DataFrame containing the data from the CSV file.
    """
    try:
        dataframe = pd.read_csv(file_path)
        logging.info(f"File {file_path} successfully loaded into a DataFrame.")
        return dataframe
    except Exception as e:
        logging.error(f"An error occurred while loading the file: {e}")
        return None


def save_dataframe_to_csv(
    dataframe: pd.DataFrame,
    file_path: str,
    mode: Literal["w", "x", "a"] = "w",
    header: bool = True,
) -> None:
    """
    Saves a Pandas DataFrame to a CSV file.

    Parameters:
    dataframe (pd.DataFrame): The DataFrame to save.
    file_path (str): The path where the CSV file will be saved.
    """
    try:
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        dataframe.to_csv(file_path, mode=mode, index=False, header=header)
        logging.info(f"DataFrame successfully saved to {file_path} in mode '{mode}'.")
    except Exception as e:
        logging.error(f"An error occurred while saving the DataFrame: {e}")


def get_outer_directory(
    current_dir: Union[str, None], levels_up: int = 1
) -> Union[str, None]:
    """
    Get the outer directory path by moving up a specified number of levels from the current directory.
    """
    try:
        if current_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        outer_dir = current_dir
        for _ in range(levels_up):
            outer_dir = os.path.dirname(outer_dir)
        return outer_dir
    except Exception as e:
        logging.error(f"Error getting outer directory: {e}")
        logging.debug(traceback.format_exc())
        return None


def gen_lstm_training_config(
    history_size_list: list,
    retention_padding_list: list,
    batch_size_list: list,
    drop_rate_list: list,
    loss_list: list,
    learning_rate_list: list,
    num_layers_list: list,
    activation_function_list: list,
    input_cols_list: list,
    hidden_neurons_list: list,
    template_lstm_config: RunConfig,
    run_id_count: int,
    run_config_dict: dict,
):
    for history_size in history_size_list:
        for retention_padding in retention_padding_list:
            for batch_size in batch_size_list:
                for drop_rate in drop_rate_list:
                    for loss in loss_list:
                        for learning_rate in learning_rate_list:
                            for num_layers in num_layers_list:
                                for activation_function in activation_function_list:
                                    for input_cols in input_cols_list:
                                        for hidden_neurons in hidden_neurons_list:
                                            temp_config = copy.deepcopy(
                                                template_lstm_config
                                            )
                                            temp_config.ml_model_config.hidden_neurons = hidden_neurons
                                            temp_config.ml_model_config.activation_function = activation_function
                                            temp_config.ml_model_config.drop_rate = (
                                                drop_rate
                                            )
                                            temp_config.ml_model_config.loss = loss
                                            temp_config.ml_model_config.learning_rate = learning_rate
                                            temp_config.ml_model_config.num_layers = (
                                                num_layers
                                            )
                                            temp_config.data_config.history_size = (
                                                history_size
                                            )
                                            temp_config.data_config.retention_padding = retention_padding
                                            temp_config.data_config.input_cols = (
                                                input_cols
                                            )
                                            temp_config.training_config.batch_size = (
                                                batch_size
                                            )
                                            run_id = f"run_{run_id_count}"
                                            run_id_count += 1
                                            run_config_dict[run_id] = (
                                                temp_config.to_dict()
                                            )


def gen_transformer_training_config(
    history_size_list: list,
    batch_size_list: list,
    d_model_list: list,
    nhead_list: list,
    dim_feedforward_list: list,
    drop_rate_list: list,
    loss_list: list,
    learning_rate_list: list,
    num_layers_list: list,
    activation_function_list: list,
    input_cols_list: list,
    template_transformer_config: RunConfig,
    run_id_count: int,
    run_config_dict: dict,
    retention_padding_list: list = [0],
):
    for history_size in history_size_list:
        for batch_size in batch_size_list:
            for d_model in d_model_list:
                for nhead in nhead_list:
                    for retention_padding in retention_padding_list:
                        for dim_feedforward in dim_feedforward_list:
                            for drop_rate in drop_rate_list:
                                for loss in loss_list:
                                    for learning_rate in learning_rate_list:
                                        for num_layers in num_layers_list:
                                            for (
                                                activation_function
                                            ) in activation_function_list:
                                                for input_cols in input_cols_list:
                                                    temp_config = copy.deepcopy(
                                                        template_transformer_config
                                                    )
                                                    temp_config.ml_model_config.d_model = (
                                                        d_model
                                                    )
                                                    temp_config.ml_model_config.nhead = (
                                                        nhead
                                                    )
                                                    temp_config.ml_model_config.dim_feedforward = dim_feedforward
                                                    temp_config.ml_model_config.activation_function = activation_function
                                                    temp_config.ml_model_config.drop_rate = drop_rate
                                                    temp_config.ml_model_config.loss = loss
                                                    temp_config.ml_model_config.learning_rate = learning_rate
                                                    temp_config.ml_model_config.num_layers = num_layers
                                                    temp_config.data_config.history_size = (
                                                        history_size
                                                    )
                                                    temp_config.data_config.retention_padding = retention_padding
                                                    temp_config.data_config.input_cols = (
                                                        input_cols
                                                    )
                                                    temp_config.training_config.batch_size = batch_size
                                                    run_id = f"run_{run_id_count}"
                                                    run_id_count += 1
                                                    run_config_dict[run_id] = (
                                                        temp_config.to_dict()
                                                    )
