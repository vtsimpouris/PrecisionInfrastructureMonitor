import argparse

from residuals import diagnose_fault


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Precision Infrastructure Monitor "
            "fault-diagnosis experiment"
        )
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose operational logging"
    )

    return parser.parse_args()


def print_diagnosis(
    title,
    residuals,
    matrix,
    thresholds=None
):
    # Find nearest known class
    nearest_fault, distance = diagnose_fault(
        residuals,
        matrix
    )

    # Optionally apply unknown-fault rejection
    if thresholds is not None:
        diagnosis, _ = diagnose_fault(
            residuals,
            matrix,
            thresholds
        )
    else:
        diagnosis = nearest_fault

    print(f"\n{title}:")
    print(residuals)

    print(
        f"Nearest known class: "
        f"{nearest_fault.upper()}"
    )

    print(
        f"Distance from signature: "
        f"{distance:.2f}"
    )

    if thresholds is not None:
        print(
            f"Acceptance threshold: "
            f"{thresholds[nearest_fault]:.2f}"
        )

    print(
        f"Diagnosis: "
        f"{diagnosis.upper()}"
    )