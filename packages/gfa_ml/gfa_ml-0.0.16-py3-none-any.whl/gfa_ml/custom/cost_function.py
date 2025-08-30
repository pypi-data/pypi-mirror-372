def d0_clo2_cost_function(current_value: float, trial_value: float) -> float:
    # Define the cost function for the d0_clo2 parameter
    return (current_value - trial_value) * 10


def d0_pulp_temp_cost_function(current_value: float, trial_value: float) -> float:
    # Define the cost function for the d0_pulp_temp parameter
    return (current_value - trial_value) * 4
