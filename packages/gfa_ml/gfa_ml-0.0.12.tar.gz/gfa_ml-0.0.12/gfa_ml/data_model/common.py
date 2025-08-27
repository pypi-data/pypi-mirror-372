from pydantic import BaseModel
from typing import Optional, Union, Dict
from typing import Type
import logging
import traceback
import os
import yaml

from gfa_ml.lib.default import (
    D_MODEL,
    DIM_FEEDFORWARD,
    HIDDEN_NEURONS,
    N_FEATURES_IMPORTANCE,
    NHEAD,
    NUM_LAYERS,
    USE_MARKERS,
)
from .data_type import ParamUnit, MetricType, ModelType

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
from gfa_ml.lib.default import (
    EPOCHS,
    BATCH_SIZE,
    LEARNING_RATE,
    DROP_RATE,
    PATIENCE,
    TEST_RATE,
    TRAIN_RATE,
    ACTIVATION_FUNCTION,
    OPTIMIZER,
    LOSS,
    LEARNING_RATE,
    VALIDATION_RATE,
    SMOOTH_WINDOW_SIZE,
    SAMPLE_SIZE,
    HISTORY_SIZE,
)


class SmoothingParam(BaseModel):
    param_name: Optional[str] = None
    description: Optional[str] = None


class MovingAverageSmoothingParam(SmoothingParam, BaseModel):
    window_size: Optional[int] = None
    min_periods: Optional[int] = None
    smoothing_type: Optional[str] = None  # e.g., "mean", "median", etc.

    def to_string(self) -> str:
        return f"MovingAverageSmoothingParam:\n window_size={self.window_size},\n min_periods={self.min_periods},\n smoothing_type={self.smoothing_type}"

    def __str__(self) -> str:
        return self.to_string()

    def to_dict(self) -> Dict[str, Union[str, int]]:
        return {
            "description": self.description,
            "window_size": self.window_size,
            "min_periods": self.min_periods,
            "smoothing_type": self.smoothing_type,
        }

    @classmethod
    def from_dict(
        cls: Type["MovingAverageSmoothingParam"], data: Dict[str, Union[str, int]]
    ) -> "MovingAverageSmoothingParam":
        try:
            return cls(
                description=data.get("description", None),
                window_size=data.get("window_size", 0),
                min_periods=data.get("min_periods", 0),
                smoothing_type=data.get("smoothing_type", None),
            )
        except Exception as e:
            logging.error(f"Error in MovingAverageSmoothingParam.from_dict: {e}")
            logging.debug(traceback.format_exc())
            return None


class SmoothFunction(BaseModel):
    function_name: str
    description: Optional[str] = None
    smoothing_param: SmoothingParam = None

    def to_string(self) -> str:
        return f"SmoothFunction:\n function_name={self.function_name},\n description={self.description},\n smoothing_param={self.smoothing_param}"

    def __str__(self) -> str:
        return self.to_string()

    def to_dict(self) -> Dict[str, Union[str, SmoothingParam]]:
        try:
            return {
                "function_name": self.function_name,
                "description": self.description,
                "smoothing_param": self.smoothing_param.to_dict()
                if self.smoothing_param
                else None,
            }
        except Exception as e:
            logging.error(f"Error in SmoothFunction.to_dict: {e}")
            logging.debug(traceback.format_exc())
            return {}

    @classmethod
    def from_dict(
        cls: Type["SmoothFunction"], data: Dict[str, Union[str, SmoothingParam]]
    ) -> "SmoothFunction":
        try:
            smoothing_param = data.get("smoothing_param")
            function_name = data.get("function_name", "")
            if isinstance(smoothing_param, dict):
                if function_name == "moving_average":
                    smoothing_param = MovingAverageSmoothingParam.from_dict(
                        smoothing_param
                    )
                else:
                    smoothing_param = SmoothingParam(**smoothing_param)
            return cls(
                function_name=data.get("function_name", ""),
                description=data.get("description", None),
                smoothing_param=smoothing_param,
            )
        except Exception as e:
            logging.error(f"Error in SmoothFunction.from_dict: {e}")
            logging.debug(traceback.format_exc())
            return None


class Metric(BaseModel):
    metric_name: Optional[str] = None
    column_name: Optional[str] = None
    en_description: Optional[str] = None
    fi_description: Optional[str] = None
    unit: Optional[Union[str, ParamUnit]] = None
    stage: Optional[str] = None
    tag: Optional[str] = None
    measurement_method: Optional[str] = None
    sort: Optional[int] = None
    display_name: Optional[str] = None
    metric_type: Optional[Union[str, MetricType]] = None
    smoothing_function: Optional[SmoothFunction] = None

    def to_string(self) -> str:
        metric_type_str = (
            self.metric_type.value
            if isinstance(self.metric_type, MetricType)
            else self.metric_type
        )
        unit_str = self.unit.value if isinstance(self.unit, ParamUnit) else self.unit
        return f"Metric:\n metric_name={self.metric_name},\n column_name={self.column_name},\n unit={unit_str}, \n stage={self.stage},\n tag={self.tag},\n measurement_method={self.measurement_method},\n sort={self.sort}, \n en_description={self.en_description},\n fi_description={self.fi_description},\n display_name={self.display_name},\n metric_type={metric_type_str}, \n smoothing_function={self.smoothing_function}"

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_dict(cls: Type["Metric"], data: Dict[str, Union[str, int]]) -> "Metric":
        try:
            if data.get("metric_type") is not None:
                try:
                    data["metric_type"] = MetricType(data["metric_type"])
                except ValueError:
                    data["metric_type"] = MetricType.UNKNOWN
            if data.get("unit") is not None:
                try:
                    data["unit"] = ParamUnit(data["unit"])
                except ValueError:
                    data["unit"] = ParamUnit.UNKNOWN
            if data.get("smoothing_function") is not None:
                data["smoothing_function"] = SmoothFunction.from_dict(
                    data["smoothing_function"]
                )
            else:
                data["smoothing_function"] = None
            return cls(
                metric_name=data.get("metric_name"),
                column_name=data.get("column_name"),
                en_description=data.get("en_description"),
                fi_description=data.get("fi_description"),
                unit=data.get("unit"),
                stage=data.get("stage"),
                tag=data.get("tag"),
                measurement_method=data.get("measurement_method"),
                sort=data.get("sort"),
                display_name=data.get("display_name"),
                metric_type=data.get("metric_type", None),
                smoothing_function=data.get("smoothing_function", None),
            )
        except Exception as e:
            logging.error(f"Error in Metric.from_dict: {e}")
            logging.info(traceback.format_exc())
            return None

    def to_dict(self) -> Dict[str, Union[str, int]]:
        if isinstance(self.unit, ParamUnit):
            unit_value = self.unit.value
        else:
            unit_value = self.unit
        if isinstance(self.metric_type, MetricType):
            metric_type_value = self.metric_type.value
        else:
            metric_type_value = self.metric_type
        if self.smoothing_function:
            smoothing_function_value = self.smoothing_function.to_dict()
        else:
            smoothing_function_value = None
        return {
            "metric_name": self.metric_name,
            "column_name": self.column_name,
            "en_description": self.en_description,
            "fi_description": self.fi_description,
            "unit": unit_value,
            "stage": self.stage,
            "tag": self.tag,
            "measurement_method": self.measurement_method,
            "sort": self.sort,
            "display_name": self.display_name,
            "metric_type": metric_type_value,
            "smoothing_function": smoothing_function_value,
        }


class StageInfo(BaseModel):
    stage_name: str
    input_parameters: Dict[str, Metric]
    quality_indicators: Dict[str, Metric]
    control_parameters: Dict[str, Metric]

    def to_string(self) -> str:
        return f"StageInfo:\n stage_name={self.stage_name},\n input_parameters={self.input_parameters},\n quality_indicators={self.quality_indicators},\n control_parameters={self.control_parameters}"

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_dict(
        cls: Type["StageInfo"], data: Dict[str, Union[str, Dict]]
    ) -> "StageInfo":
        try:
            input_parameters = {
                k: Metric(**v) for k, v in data.get("input_parameters", {}).items()
            }
            quality_indicators = {
                k: Metric(**v) for k, v in data.get("quality_indicators", {}).items()
            }
            control_parameters = {
                k: Metric(**v) for k, v in data.get("control_parameters", {}).items()
            }
            return cls(
                stage_name=data["stage_name"],
                input_parameters=input_parameters,
                quality_indicators=quality_indicators,
                control_parameters=control_parameters,
            )
        except Exception as e:
            logging.error(f"Error in StageInfo.from_dict: {e}")
            logging.debug(traceback.format_exc())
            return None


class MultiStageInfo(BaseModel):
    stages: Dict[str, StageInfo]

    def to_string(self) -> str:
        return f"MultiStageInfo:\n stages={self.stages}"

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_dict(
        cls: Type["MultiStageInfo"], data: Dict[str, Union[str, Dict]]
    ) -> "MultiStageInfo":
        try:
            stages = {
                k: StageInfo.from_dict(v) for k, v in data.get("stages", {}).items()
            }
            return cls(stages=stages)
        except Exception as e:
            logging.error(f"Error in MultiStageInfo.from_dict: {e}")
            logging.debug(traceback.format_exc())
            return None

    def get_stage(self, stage_name: str) -> Optional[StageInfo]:
        return self.stages.get(stage_name)


class MetricReport(BaseModel):
    metric_name: str
    total_count: int
    missing_count: int
    missing_rate: float
    zero_count: Optional[int] = None
    zero_rate: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    value_range: Optional[float] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    standard_deviation: Optional[float] = None
    variance: Optional[float] = None
    quantile_25th: Optional[float] = None
    quantile_75th: Optional[float] = None
    interquartile_range: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    positive_count: Optional[int] = None
    negative_count: Optional[int] = None
    positive_rate: Optional[float] = None
    negative_rate: Optional[float] = None
    mean_measurement_interval: Optional[float] = None
    min_measurement_interval: Optional[float] = None
    max_measurement_interval: Optional[float] = None

    def to_string(self) -> str:
        return (
            f"MetricReport:\n"
            f" metric_name={self.metric_name},\n"
            f" total_count={self.total_count},\n"
            f" missing_count={self.missing_count},\n"
            f" missing_rate={self.missing_rate},\n"
            f" zero_count={self.zero_count},\n"
            f" zero_rate={self.zero_rate},\n"
            f" min_value={self.min_value},\n"
            f" max_value={self.max_value},\n"
            f" value_range={self.value_range},\n"
            f" mean_value={self.mean_value},\n"
            f" median_value={self.median_value},\n"
            f" standard_deviation={self.standard_deviation},\n"
            f" variance={self.variance},\n"
            f" quantile_25th={self.quantile_25th},\n"
            f" quantile_75th={self.quantile_75th},\n"
            f" interquartile_range={self.interquartile_range},\n"
            f" skewness={self.skewness},\n"
            f" kurtosis={self.kurtosis},\n"
            f" positive_count={self.positive_count},\n"
            f" negative_count={self.negative_count},\n"
            f" positive_rate={self.positive_rate},\n"
            f" negative_rate={self.negative_rate},\n"
            f" mean_measurement_interval={self.mean_measurement_interval},\n"
            f" min_measurement_interval={self.min_measurement_interval},\n"
            f" max_measurement_interval={self.max_measurement_interval}"
        )

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_dict(
        cls: Type["MetricReport"], data: Dict[str, Union[str, int, float]]
    ) -> "MetricReport":
        try:
            return cls(
                metric_name=data.get("metric_name", ""),
                total_count=data.get("total_count", 0),
                missing_count=data.get("missing_count", 0),
                missing_rate=data.get("missing_rate", 0.0),
                zero_count=data.get("zero_count", None),
                zero_rate=data.get("zero_rate", None),
                min_value=data.get("min_value", None),
                max_value=data.get("max_value", None),
                value_range=data.get("value_range", None),
                mean_value=data.get("mean_value", None),
                median_value=data.get("median_value", None),
                standard_deviation=data.get("standard_deviation", None),
                variance=data.get("variance", None),
                quantile_25th=data.get("quantile_25th", None),
                quantile_75th=data.get("quantile_75th", None),
                interquartile_range=data.get("interquartile_range", None),
                skewness=data.get("skewness", None),
                kurtosis=data.get("kurtosis", None),
                positive_count=data.get("positive_count", None),
                negative_count=data.get("negative_count", None),
                positive_rate=data.get("positive_rate", None),
                negative_rate=data.get("negative_rate", None),
                mean_measurement_interval=data.get("mean_measurement_interval", None),
                min_measurement_interval=data.get("min_measurement_interval", None),
                max_measurement_interval=data.get("max_measurement_interval", None),
            )
        except Exception as e:
            logging.error(f"Error in MetricReport.from_dict: {e}")
            logging.debug(traceback.format_exc())
            return None

    def to_dict(self) -> Dict[str, Union[str, int, float]]:
        return {
            "metric_name": self.metric_name,
            "total_count": self.total_count,
            "missing_count": self.missing_count,
            "missing_rate": self.missing_rate,
            "zero_count": self.zero_count,
            "zero_rate": self.zero_rate,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "value_range": self.value_range,
            "mean_value": self.mean_value,
            "median_value": self.median_value,
            "standard_deviation": self.standard_deviation,
            "variance": self.variance,
            "quantile_25th": self.quantile_25th,
            "quantile_75th": self.quantile_75th,
            "interquartile_range": self.interquartile_range,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "positive_rate": self.positive_rate,
            "negative_rate": self.negative_rate,
            "mean_measurement_interval": self.mean_measurement_interval,
            "min_measurement_interval": self.min_measurement_interval,
            "max_measurement_interval": self.max_measurement_interval,
        }

    def save_to_yaml(self, file_path: str):
        try:
            save_dir = os.path.dirname(file_path)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            with open(file_path, "w") as file:
                yaml.dump(self.to_dict(), file, sort_keys=False)
            logging.info(f"MetricReport saved to {file_path}")
        except Exception as e:
            logging.error(f"Error saving MetricReport to YAML: {e}")
            logging.debug(traceback.format_exc())


class DataConfig(BaseModel):
    train_ratio: Optional[float] = TRAIN_RATE
    validation_ratio: Optional[float] = VALIDATION_RATE
    test_ratio: Optional[float] = TEST_RATE
    history_size: Optional[int] = HISTORY_SIZE
    input_cols: Optional[list] = None
    output_col: Optional[str] = None
    index_col: Optional[str] = None
    retention_col: Optional[str] = None
    retention_padding: Optional[int] = 0

    @classmethod
    def from_dict(
        cls: Type["DataConfig"], data: Dict[str, Union[str, float, int]]
    ) -> "DataConfig":
        return cls(
            train_ratio=data.get("train_ratio", TRAIN_RATE),
            validation_ratio=data.get("validation_ratio", VALIDATION_RATE),
            test_ratio=data.get("test_ratio", TEST_RATE),
            history_size=data.get("history_size", HISTORY_SIZE),
            input_cols=data.get("input_cols", None),
            output_col=data.get("output_col", None),
            index_col=data.get("index_col", None),
            retention_col=data.get("retention_col", None),
            retention_padding=data.get("retention_padding", 0),
        )

    def to_dict(self):
        return {
            "train_ratio": self.train_ratio,
            "validation_ratio": self.validation_ratio,
            "test_ratio": self.test_ratio,
            "history_size": self.history_size,
            "input_cols": self.input_cols,
            "output_col": self.output_col,
            "index_col": self.index_col,
            "retention_col": self.retention_col,
            "retention_padding": self.retention_padding,
        }

    def to_string(self) -> str:
        return f"DataConfig:\n train_ratio={self.train_ratio},\n validation_ratio={self.validation_ratio},\n test_ratio={self.test_ratio},\n history_size={self.history_size},\n input_cols={self.input_cols},\n output_col={self.output_col},\n index_col={self.index_col},\n retention_col={self.retention_col},\n retention_padding={self.retention_padding}"

    def __str__(self) -> str:
        return self.to_string()


class TrainingConfig(BaseModel):
    epochs: Optional[int] = EPOCHS
    batch_size: Optional[int] = BATCH_SIZE
    patience: Optional[int] = PATIENCE
    sample_size: Optional[int] = SAMPLE_SIZE
    n_features_importance: Optional[int] = N_FEATURES_IMPORTANCE
    use_markers: Optional[bool] = USE_MARKERS
    smooth_window_size: Optional[int] = SMOOTH_WINDOW_SIZE
    plot: bool = True

    def to_string(self) -> str:
        return f"TrainingConfig:\n epochs={self.epochs},\n batch_size={self.batch_size},\n patience={self.patience},\n sample_size={self.sample_size},\n n_features_importance={self.n_features_importance},\n use_markers={self.use_markers},\n smooth_window_size={self.smooth_window_size},\n plot={self.plot}"

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_dict(
        cls: Type["TrainingConfig"], data: Dict[str, Union[str, float, int]]
    ) -> "TrainingConfig":
        return cls(
            epochs=data.get("epochs", EPOCHS),
            batch_size=data.get("batch_size", BATCH_SIZE),
            patience=data.get("patience", PATIENCE),
            sample_size=data.get("sample_size", SAMPLE_SIZE),
            n_features_importance=data.get(
                "n_features_importance", N_FEATURES_IMPORTANCE
            ),
            use_markers=data.get("use_markers", USE_MARKERS),
            smooth_window_size=data.get("smooth_window_size", SMOOTH_WINDOW_SIZE),
            plot=data.get("plot", True),
        )

    def to_dict(self):
        return {
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "patience": self.patience,
            "sample_size": self.sample_size,
            "n_features_importance": self.n_features_importance,
            "use_markers": self.use_markers,
            "smooth_window_size": self.smooth_window_size,
            "plot": self.plot,
        }


class ModelConfig(BaseModel):
    model_type: Optional[ModelType] = None
    drop_rate: Optional[float] = DROP_RATE
    optimizer: Optional[str] = OPTIMIZER
    loss: Optional[str] = LOSS
    activation_function: Optional[str] = ACTIVATION_FUNCTION
    learning_rate: Optional[float] = LEARNING_RATE
    num_layers: Optional[int] = NUM_LAYERS

    @classmethod
    def from_dict(
        cls: Type["ModelConfig"], data: Dict[str, Union[str, float, int]]
    ) -> "ModelConfig":
        return cls(
            model_type=data.get("model_type", None),
            drop_rate=data.get("drop_rate", DROP_RATE),
            optimizer=data.get("optimizer", OPTIMIZER),
            loss=data.get("loss", LOSS),
            activation_function=data.get("activation_function", ACTIVATION_FUNCTION),
            learning_rate=data.get("learning_rate", LEARNING_RATE),
            num_layers=data.get("num_layers", NUM_LAYERS),
        )

    def to_dict(self):
        return {
            "model_type": self.model_type.value,
            "drop_rate": self.drop_rate,
            "optimizer": self.optimizer,
            "loss": self.loss,
            "activation_function": self.activation_function,
            "learning_rate": self.learning_rate,
            "num_layers": self.num_layers,
        }


class LSTMConfig(ModelConfig):
    hidden_neurons: Optional[int] = HIDDEN_NEURONS

    @classmethod
    def from_dict(
        cls: Type["LSTMConfig"], data: Dict[str, Union[str, float, int]]
    ) -> "LSTMConfig":
        return cls(
            hidden_neurons=data.get("hidden_neurons", HIDDEN_NEURONS),
            **ModelConfig.from_dict(data).to_dict(),
        )

    def to_dict(self):
        return {"hidden_neurons": self.hidden_neurons, **ModelConfig.to_dict(self)}


class TransformerConfig(ModelConfig):
    d_model: Optional[int] = D_MODEL
    nhead: Optional[int] = NHEAD
    dim_feedforward: Optional[int] = DIM_FEEDFORWARD

    @classmethod
    def from_dict(
        cls: Type["TransformerConfig"], data: Dict[str, Union[str, float, int]]
    ) -> "TransformerConfig":
        return cls(
            d_model=data.get("d_model", D_MODEL),
            nhead=data.get("nhead", NHEAD),
            dim_feedforward=data.get("dim_feedforward", DIM_FEEDFORWARD),
            **ModelConfig.from_dict(data).to_dict(),
        )

    def to_dict(self):
        return {
            "d_model": self.d_model,
            "nhead": self.nhead,
            "dim_feedforward": self.dim_feedforward,
            **ModelConfig.to_dict(self),
        }

    def to_string(self) -> str:
        return f"TransformerConfig:\n d_model={self.d_model},\n nhead={self.nhead},\n dim_feedforward={self.dim_feedforward},\n {ModelConfig.to_string(self)}"

    def __str__(self) -> str:
        return self.to_string()


class RunConfig(BaseModel):
    data_config: Optional[DataConfig] = None
    training_config: Optional[TrainingConfig] = None
    ml_model_config: Optional[ModelConfig] = None

    def to_string(self) -> str:
        return f"RunConfig:\n data_config={self.data_config},\n training_config={self.training_config},\n ml_model_config={self.ml_model_config}"

    def __str__(self) -> str:
        return self.to_string()

    def to_dict(self) -> Dict[str, Dict]:
        return {
            "data_config": self.data_config.to_dict() if self.data_config else None,
            "training_config": self.training_config.to_dict()
            if self.training_config
            else None,
            "ml_model_config": self.ml_model_config.to_dict()
            if self.ml_model_config
            else None,
        }

    @classmethod
    def from_dict(cls: Type["RunConfig"], data: Dict[str, Dict]) -> "RunConfig":
        ml_model_config_dict = data.get("ml_model_config", {})
        model_type = ml_model_config_dict.get("model_type", None)
        if model_type == "lstm":
            ml_model_config = LSTMConfig.from_dict(ml_model_config_dict)
        elif model_type == "transformer":
            ml_model_config = TransformerConfig.from_dict(ml_model_config_dict)
        else:
            ml_model_config = ModelConfig.from_dict(ml_model_config_dict)

        data_config_dict = data.get("data_config", {})
        data_config = DataConfig.from_dict(data_config_dict)

        training_config_dict = data.get("training_config", {})
        training_config = TrainingConfig.from_dict(training_config_dict)

        return cls(
            data_config=data_config,
            training_config=training_config,
            ml_model_config=ml_model_config,
        )

    @classmethod
    def from_yaml(cls: Type["RunConfig"], file_path: str) -> "RunConfig":
        try:
            with open(file_path) as file:
                data = yaml.safe_load(file)
            return cls.from_dict(data)
        except Exception as e:
            logging.error(f"Error loading RunConfig from YAML: {e}")
            logging.info(traceback.format_exc())
            return None
