import logging
import time

import requests

from config import (
    BASE_URL,
    REQUEST_TIMEOUT
)

from docker_utils import container_running


logger = logging.getLogger(__name__)


def probe_system():

    result = {
        "heartbeat": container_running(),
        "configValid": None,
        "httpStatus": None,
        "latencyMs": None,
        "httpOutcome": None
    }

    # Runtime/container check
    if not result["heartbeat"]:

        logger.info(
            "Container heartbeat lost"
        )

        result["httpOutcome"] = "runtime_down"

        return result

    # Config check
    try:
        response = requests.get(
            f"{BASE_URL}/config/health",
            timeout=REQUEST_TIMEOUT
        )

        result["configValid"] = (
            response.json()["valid"]
        )

        if result["configValid"] is False:
            logger.info(
                "Configuration health check failed"
            )

    except requests.RequestException as exception:

        logger.warning(
            "Could not retrieve config health: %s",
            exception
        )

        result["configValid"] = None

    # HTTP/network/service check
    try:
        start = time.perf_counter()

        response = requests.get(
            f"{BASE_URL}/measurements",
            timeout=REQUEST_TIMEOUT
        )

        result["latencyMs"] = (
            time.perf_counter() - start
        ) * 1000

        result["httpStatus"] = (
            response.status_code
        )

        if response.status_code == 200:

            result["httpOutcome"] = "ok"

            logger.debug(
                "Measurement request successful: "
                "status=%d latency=%.2f ms",
                response.status_code,
                result["latencyMs"]
            )

        elif response.status_code >= 500:

            result["httpOutcome"] = (
                "server_error"
            )

            logger.info(
                "Measurement API returned server error: %d",
                response.status_code
            )

        else:

            result["httpOutcome"] = (
                "http_error"
            )

            logger.warning(
                "Measurement API returned unexpected status: %d",
                response.status_code
            )

    except requests.Timeout:

        logger.info(
            "Measurement request timed out after %.2f s",
            REQUEST_TIMEOUT
        )

        result["httpOutcome"] = "timeout"

    except requests.ConnectionError as exception:

        logger.info(
            "Could not connect to measurement API: %s",
            exception
        )

        result["httpOutcome"] = (
            "connection_error"
        )

    return result