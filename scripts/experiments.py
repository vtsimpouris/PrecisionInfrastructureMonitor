import json

from config import REPO_ROOT
from fault_injection import SCENARIOS
from residuals import calculate_residuals
import logging

logger = logging.getLogger(__name__)

def run_experiments(runs_per_fault):

    results = {}

    for scenario_name, scenario in SCENARIOS.items():

        print(
            f"Injecting {scenario_name.upper():<8} "
            f"[{runs_per_fault} runs]... ",
            end="",
            flush=True
        )

        logger.info(
            "Starting experiment: %s",
            scenario_name.upper()
        )

        scenario_results = []

        for run_number in range(runs_per_fault):

            logger.info(
                "[%s] Run %d/%d",
                scenario_name.upper(),
                run_number + 1,
                runs_per_fault
            )

            observation = scenario()

            residuals = calculate_residuals(
                observation
            )

            scenario_results.append({
                "observation": observation,
                "residuals": residuals
            })

        results[scenario_name] = scenario_results

        logger.info(
            "Completed experiment: %s",
            scenario_name.upper()
        )

        print("done")

    return results


def save_results(results, matrix):

    experiment_path = (
        REPO_ROOT / "experiment_results.json"
    )

    matrix_path = (
        REPO_ROOT / "sensitivity_matrix.json"
    )

    experiment_path.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8"
    )

    matrix_path.write_text(
        json.dumps(matrix, indent=2),
        encoding="utf-8"
    )

    print(
        f"\nExperiment results: {experiment_path}"
    )

    print(
        f"Sensitivity matrix: {matrix_path}"
    )