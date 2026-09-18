import json

import requests
import random
import threading
import time
import logging

logger = logging.getLogger(__name__)

from config import (
    BASE_URL,
    RUNTIME_CONFIG_PATH,
    GOOD_CALIBRATION_PATH,
    BAD_CALIBRATION_PATH
)

from docker_utils import (
    stop_container,
    start_container,
    wait_for_service,
    container_running
)

from probing import probe_system


def set_config(calibration_path):
    config = {
        "CalibrationPath": calibration_path
    }

    RUNTIME_CONFIG_PATH.write_text(
        json.dumps(config, indent=2),
        encoding="utf-8"
    )


def reset_system():

    # Restore healthy configuration
    set_config(GOOD_CALIBRATION_PATH)

    # Ensure runtime is alive
    start_container()

    if not wait_for_service():
        raise RuntimeError(
            "C# service did not become available."
        )

    # Reset internal C# fault switches
    requests.post(
        f"{BASE_URL}/faults/reset",
        timeout=2
    )


def healthy_scenario():
    reset_system()

    return probe_system()


def service_fault():
    reset_system()
    logger.info(
        "Injecting service failure"
    )
    requests.post(
        f"{BASE_URL}/faults/service/true",
        timeout=2
    )

    return probe_system()


def config_fault():
    reset_system()
    logger.info(
        "Injecting invalid configuration"
    )
    set_config(BAD_CALIBRATION_PATH)

    return probe_system()


def network_fault():
    reset_system()

    delay_ms = random.randint(700, 1300)
    logger.info(
        "Injecting network delay: %d ms",
        delay_ms
    )
    requests.post(
        f"{BASE_URL}/faults/network/{delay_ms}",
        timeout=2
    )

    observation = probe_system()

    observation["injectedDelayMs"] = delay_ms

    return observation


def runtime_fault():
    reset_system()

    downtime = random.uniform(0.3, 1.0)
    logger.info(
        "Injecting runtime outage: %.2f s",
        downtime
    )
    def cause_runtime_outage():
        stop_container()
        time.sleep(downtime)
        start_container()

    fault_thread = threading.Thread(
        target=cause_runtime_outage
    )

    fault_thread.start()

    heartbeat_checks = 10
    heartbeat_losses = 0

    for _ in range(heartbeat_checks):

        if not container_running():
            heartbeat_losses += 1

        time.sleep(0.1)

    fault_thread.join()

    return {
        "heartbeat": container_running(),
        "heartbeatLossRate":
            heartbeat_losses / heartbeat_checks,
        "configValid": None,
        "httpStatus": None,
        "latencyMs": None,
        "httpOutcome": "runtime_instability"
    }


SCENARIOS = {
    "healthy": healthy_scenario,
    "service": service_fault,
    "config": config_fault,
    "network": network_fault,
    "runtime": runtime_fault
}