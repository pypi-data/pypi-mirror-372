import optuna

# optuna.logging.set_verbosity(optuna.logging.ERROR)
from gfa_ml.data_model.data_type import OptimizationObjective, OptunaSampler
from gfa_ml.data_model.common import OutputConstraint, OutputQuality
from gfa_ml.data_model.common import InputSpecification, ControlParameter
import pandas as pd
from gfa_ml.lib.data_processing import create_inference_input
from gfa_ml.lib.common import make_prediction
import logging
import traceback
import importlib

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ControlParameterOptimizer:
    def __init__(
        self,
        input_df: pd.DataFrame,
        model_dict: dict,
        history_size: int,
        input_spec: InputSpecification,
        output_constraints: OutputConstraint,
        cost_optimization_objective: OutputQuality = None,
    ):
        self.input_df = input_df
        self.model_dict = model_dict
        self.history_size = history_size
        self.input_spec = input_spec
        self.output_constraints = output_constraints
        self.cost_optimization_objective = cost_optimization_objective
        self.control_parameters_spec = {}
        if cost_optimization_objective != None:
            self.output_constraints.constraint[
                cost_optimization_objective.parameter_name
            ] = cost_optimization_objective

        for parameter in self.input_spec.specification.values():
            if isinstance(parameter, ControlParameter):
                self.control_parameters_spec[parameter.parameter_name] = parameter

    def get_directions(self) -> list[str]:
        try:
            """Return a list of 'maximize'/'minimize' for objectives."""
            directions = []
            for quality in self.output_constraints.constraint.values():
                if quality.objective != OptimizationObjective.NONE:
                    directions.append(quality.objective.value)
            return directions
        except Exception as e:
            logging.error(f"Error getting directions: {e}")
            logging.info(traceback.format_exc())
            return []

    def pick_objectives(self, result: dict):
        try:
            """Return actual objective values for a trial."""
            objectives = []
            for name, quality in self.output_constraints.constraint.items():
                if quality.objective != OptimizationObjective.NONE:
                    objectives.append(result[name])
            return objectives
        except Exception as e:
            logging.error(f"Error picking objectives: {e}")
            logging.info(traceback.format_exc())
            return []

    def compute_constraints(self, result: dict) -> list[float]:
        try:
            """Convert black-box outputs into Optuna constraint values."""
            values = []
            for name, quality in self.output_constraints.constraint.items():
                val = result[name]

                # check upper bound
                if quality.upper_limit is not None:
                    values.append(val - quality.upper_limit)

                # check lower bound
                if quality.lower_limit is not None:
                    values.append(quality.lower_limit - val)
            return values
        except Exception as e:
            logging.error(f"Error computing constraints: {e}")
            logging.info(traceback.format_exc())
            return []

    def __call__(self, trial: optuna.Trial) -> float:
        try:
            # Define the search space
            for parameter in self.control_parameters_spec.values():
                parameter.trial_value = trial.suggest_float(
                    parameter.parameter_name,
                    parameter.min_value,
                    parameter.max_value,
                    step=parameter.step_size,
                )

            input_data = create_inference_input(
                self.input_df, self.history_size, self.input_spec, trial_run=True
            )

            result = make_prediction(input_data, self.model_dict)
            if self.cost_optimization_objective != None:
                cost_saving = 0
                for parameter in self.control_parameters_spec.values():
                    if parameter.cost_function != None:
                        cost_function_module = importlib.import_module(
                            "gfa_ml.custom.cost_function"
                        )
                        cost_function = getattr(
                            cost_function_module, parameter.cost_function
                        )
                        cost_saving += cost_function(
                            parameter.current_value, parameter.trial_value
                        )
                result[self.cost_optimization_objective.parameter_name] = cost_saving

            # define objective
            constraints = self.compute_constraints(result)
            trial.set_user_attr("constraints", constraints)

            objectives = self.pick_objectives(result)
            return tuple(objectives)
        except Exception as e:
            logging.error(f"Error during trial evaluation: {e}")
            logging.info(traceback.format_exc())
            return ()

    def optimize(
        self, n_trials: int = 50, sampler_type: OptunaSampler = OptunaSampler.QMCSampler
    ) -> optuna.Study:
        try:
            directions = self.get_directions()
            if sampler_type == OptunaSampler.TPE:
                sampler = optuna.samplers.TPESampler()
            elif sampler_type == OptunaSampler.CMAES:
                sampler = optuna.samplers.CmaEsSampler()
            elif sampler_type == OptunaSampler.QMCSampler:
                sampler = optuna.samplers.QMCSampler()
            elif sampler_type == OptunaSampler.GRID:
                sampler = optuna.samplers.GridSampler()
            elif sampler_type == OptunaSampler.RANDOM:
                sampler = optuna.samplers.RandomSampler()
            elif sampler_type == OptunaSampler.NSGAII:
                sampler = optuna.samplers.NSGAIISampler()
            elif sampler_type == OptunaSampler.BRUTE_FORCE:
                sampler = optuna.samplers.BruteForceSampler()
            elif sampler_type == OptunaSampler.BOTORCH:
                sampler = optuna.samplers.BoTorchSampler()
            elif sampler_type == OptunaSampler.GP:
                sampler = optuna.samplers.GPSampler()
            else:
                sampler = optuna.samplers.TPESampler()

            study = optuna.create_study(directions=directions, sampler=sampler)
            # --- Run optimization ---
            study.optimize(self, n_trials=n_trials)
            return study
        except Exception as e:
            logging.error(f"Error during optimization: {e}")
            logging.info(traceback.format_exc())
            return None
