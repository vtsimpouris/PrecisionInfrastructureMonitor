def calculate_residuals(observation):

    return {
        "httpFailure":
            0
            if observation["httpStatus"] == 200
            else 1,

        "configInvalid":
            1
            if observation["configValid"] is False
            else 0,

        "networkTimeout":
            1
            if observation["httpOutcome"] == "timeout"
            else 0,

        "HeartbeatLost":
            observation.get("heartbeatLossRate", 0.0)
    }


def build_sensitivity_matrix(results):

    residual_names = [
        "httpFailure",
        "configInvalid",
        "networkTimeout",
        "HeartbeatLost"
    ]

    fault_names = [
        "service",
        "config",
        "network",
        "runtime"
    ]

    matrix = {}

    for residual_name in residual_names:

        matrix[residual_name] = {}

        for fault_name in fault_names:

            runs = results[fault_name]

            mean_response = sum(
                run["residuals"][residual_name]
                for run in runs
            ) / len(runs)

            matrix[residual_name][fault_name] = (
                mean_response
            )

    return matrix


def print_sensitivity_matrix(matrix):

    faults = [
        "service",
        "config",
        "network",
        "runtime"
    ]

    print("\nSensitivity Matrix S\n")

    print(
        f"{'Residual':<22}"
        + "".join(
            f"{fault:<12}"
            for fault in faults
        )
    )

    print("-" * 70)

    for residual, values in matrix.items():

        print(
            f"{residual:<22}"
            + "".join(
                f"{values[fault]:<12.2f}"
                for fault in faults
            )
        )

import math


def diagnose_fault(
    observed_residuals,
    matrix,
    thresholds=None
):

    residual_names = [
        "httpFailure",
        "configInvalid",
        "networkTimeout",
        "HeartbeatLost"
    ]

    # All residuals healthy
    if all(
        observed_residuals[name] == 0
        for name in residual_names
    ):
        return "healthy", 0.0

    distances: dict[str, float] = {}

    for fault_name in matrix["httpFailure"].keys():
        distance_squared = 0.0

        for residual_name in residual_names:
            observed = observed_residuals[residual_name]
            expected = matrix[residual_name][fault_name]

            distance_squared += (
                                        observed - expected
                                ) ** 2

        distances[fault_name] = math.sqrt(distance_squared)

    best_fault = min(
        distances,
        key=lambda fault: distances[fault]
    )

    best_distance = distances[best_fault]

    if thresholds is not None:
        threshold = thresholds.get(best_fault)

        if (
                threshold is not None
                and best_distance > threshold
        ):
            return "unknown", best_distance

    return best_fault, best_distance