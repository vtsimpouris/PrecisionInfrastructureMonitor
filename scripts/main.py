import argparse

from logging_config import setup_logging

from config import RUNS_PER_FAULT

from experiments import (
    run_experiments,
    save_results
)

from fault_injection import reset_system

from residuals import (
    build_sensitivity_matrix,
    print_sensitivity_matrix,
    diagnose_fault
)

from validation import (
    run_blind_validation,
    print_confusion_matrix,
    calculate_distance_thresholds
)

from helpers import (
    parse_args,
    print_diagnosis
)

def main():

    args = parse_args()

    setup_logging(
        verbose=args.verbose
    )

    try:
        ...
        results = run_experiments(
            RUNS_PER_FAULT
        )

        matrix = build_sensitivity_matrix(
            results
        )

        save_results(
            results,
            matrix
        )

        accuracy, confusion, correct_distances = run_blind_validation(
            matrix,
            runs=100
        )

        thresholds = calculate_distance_thresholds(
            correct_distances,
            percentile=0.95
        )

        print_sensitivity_matrix(
            matrix
        )

        print("\nDistance thresholds")

        for fault_name, threshold in thresholds.items():
            if threshold is None:
                print(f"{fault_name:<10} no data")
            else:
                print(
                    f"{fault_name:<10} "
                    f"{threshold:.2f}"
                )

        print_confusion_matrix(confusion)

        print(
            f"\nDiagnostic accuracy: "
            f"{accuracy * 100:.1f}%"
        )

        unseen_residuals = {
            "httpFailure": 1,
            "configInvalid": 0,
            "networkTimeout": 1,
            "HeartbeatLost": 0
        }

        print_diagnosis(
            "Unseen residual vector",
            unseen_residuals,
            matrix,
            thresholds
        )

        novel_residuals = {
            "httpFailure": 0,
            "configInvalid": 1,
            "networkTimeout": 1,
            "HeartbeatLost": 1
        }

        print_diagnosis(
            "Novel residual vector",
            novel_residuals,
            matrix,
            thresholds
        )

    finally:
        print(
            "\nRestoring healthy system..."
        )

        reset_system()


if __name__ == "__main__":
    main()