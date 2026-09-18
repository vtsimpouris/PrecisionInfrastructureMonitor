import logging
import subprocess
import time

import requests

from config import (
    BASE_URL,
    CONTAINER_NAME
)


logger = logging.getLogger(__name__)


def container_running():

    result = subprocess.run(
        [
            "docker",
            "inspect",
            "-f",
            "{{.State.Running}}",
            CONTAINER_NAME
        ],
        capture_output=True,
        text=True
    )

    running = (
        result.returncode == 0
        and result.stdout.strip() == "true"
    )

    logger.debug(
        "Container %s running=%s",
        CONTAINER_NAME,
        running
    )

    return running


def start_container():

    if not container_running():

        logger.info(
            "Starting Docker container: %s",
            CONTAINER_NAME
        )

        subprocess.run(
            [
                "docker",
                "start",
                CONTAINER_NAME
            ],
            check=True,
            capture_output=True
        )

        logger.info(
            "Docker container started: %s",
            CONTAINER_NAME
        )


def stop_container():

    if container_running():

        logger.info(
            "Stopping Docker container: %s",
            CONTAINER_NAME
        )

        subprocess.run(
            [
                "docker",
                "stop",
                CONTAINER_NAME
            ],
            check=True,
            capture_output=True
        )

        logger.info(
            "Docker container stopped: %s",
            CONTAINER_NAME
        )


def wait_for_service(
    timeout_seconds=5
):

    logger.debug(
        "Waiting for service to become available"
    )

    start = time.perf_counter()

    while (
        time.perf_counter() - start
        < timeout_seconds
    ):

        try:
            requests.get(
                f"{BASE_URL}/config/health",
                timeout=0.5
            )

            logger.debug(
                "Service is available"
            )

            return True

        except requests.RequestException:
            time.sleep(0.2)

    logger.error(
        "Service did not become available "
        "within %.1f seconds",
        timeout_seconds
    )

    return False