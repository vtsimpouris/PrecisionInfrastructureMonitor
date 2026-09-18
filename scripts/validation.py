import logging
import math
import random

from fault_injection import SCENARIOS
from residuals import (
    calculate_residuals,
    diagnose_fault
)


logger = logging.getLogger(__name__)


FAULT_NAMES = [
    "service",
    "config",
    "network",
    "runtime"
]


def run_blind_validation(
    matrix,
    runs=100
):
    correct = 0

    confusion = {
        actual: {
            predicted: 0
            for predicted in FAULT_NAMES + ["healthy"]
        }
        for actual in FAULT_NAMES
    }

    correct_distances = {
        fault: []
        for fault in FAULT_NAMES
    }

    print(
        f"\nRunning blind validation "
        f"[{runs} runs]... ",
        end="",
        flush=True
    )

    logger.info(
        "Starting blind validation: %d runs",
        runs
    )

    for run_number in range(runs):

        actual_fault = random.choice(
            FAULT_NAMES
        )

        observation = SCENARIOS[
            actual_fault
        ]()

        residuals = calculate_residuals(
            observation
        )

        predicted_fault, distance = diagnose_fault(
            residuals,
            matrix
        )

        confusion[
            actual_fault
        ][
            predicted_fault
        ] += 1

        if predicted_fault == actual_fault:

            correct += 1

            correct_distances[
                actual_fault
            ].append(distance)

        logger.info(
            "[%3d/%d] Actual=%-8s "
            "Predicted=%-8s Distance=%.2f",
            run_number + 1,
            runs,
            actual_fault,
            predicted_fault,
            distance
        )

    accuracy = correct / runs

    logger.info(
        "Blind validation completed: "
        "accuracy=%.1f%%",
        accuracy * 100
    )

    print("done")

    return (
        accuracy,
        confusion,
        correct_distances
    )


def calculate_distance_thresholds(
    correct_distances,
    percentile=0.95
):
    thresholds = {}

    for fault, distances in (
        correct_distances.items()
    ):

        if not distances:
            thresholds[fault] = None
            continue

        sorted_distances = sorted(
            distances
        )

        index = math.ceil(
            percentile
            * len(sorted_distances)
        ) - 1

        thresholds[fault] = (
            sorted_distances[index]
        )

    return thresholds


def print_confusion_matrix(
    confusion
):

    predicted_names = (
        FAULT_NAMES
        + ["healthy"]
    )

    print(
        "\nConfusion Matrix\n"
    )

    width = 12

    print(
        f"{'Actual':<{width}}"
        + "".join(
            f"{name:<{width}}"
            for name
            in predicted_names
        )
    )

    print(
        "-"
        * (
            width
            * (
                len(predicted_names)
                + 1
            )
        )
    )

    for actual in FAULT_NAMES:

        print(
            f"{actual:<{width}}"
            + "".join(
                f"{confusion[actual][predicted]:<{width}}"
                for predicted
                in predicted_names
            )
        )