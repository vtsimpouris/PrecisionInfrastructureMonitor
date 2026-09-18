import pytest
import requests

from config import BASE_URL, BAD_CALIBRATION_PATH
from docker_utils import (
    container_running,
    stop_container,
    start_container,
    wait_for_service
)
from fault_injection import (
    reset_system,
    set_config
)


@pytest.fixture(autouse=True)
def clean_system():
    """
    Start every test healthy and restore the system afterward.
    """
    reset_system()

    yield

    reset_system()


def test_healthy_system():

    config_response = requests.get(
        f"{BASE_URL}/config/health",
        timeout=2
    )

    measurement_response = requests.get(
        f"{BASE_URL}/measurements",
        timeout=2
    )

    assert config_response.status_code == 200
    assert config_response.json()["valid"] is True

    assert measurement_response.status_code == 200

    measurement = measurement_response.json()

    assert "xOffset" in measurement
    assert "yOffset" in measurement
    assert measurement["status"] == "OK"


def test_service_fault_produces_server_errors():

    requests.post(
        f"{BASE_URL}/faults/service/true",
        timeout=2
    )

    statuses = []

    # Service fault is intentionally intermittent.
    for _ in range(20):

        response = requests.get(
            f"{BASE_URL}/measurements",
            timeout=2
        )

        statuses.append(response.status_code)

    assert 500 in statuses


def test_config_fault():

    set_config(BAD_CALIBRATION_PATH)

    config_response = requests.get(
        f"{BASE_URL}/config/health",
        timeout=2
    )

    measurement_response = requests.get(
        f"{BASE_URL}/measurements",
        timeout=2
    )

    assert config_response.json()["valid"] is False
    assert measurement_response.status_code == 500


def test_network_timeout():

    requests.post(
        f"{BASE_URL}/faults/network/1500",
        timeout=2
    )

    with pytest.raises(requests.Timeout):

        requests.get(
            f"{BASE_URL}/measurements",
            timeout=0.5
        )


def test_runtime_failure():

    stop_container()

    assert container_running() is False

    with pytest.raises(
        requests.ConnectionError
    ):

        requests.get(
            f"{BASE_URL}/measurements",
            timeout=1
        )

    start_container()

    assert wait_for_service(
        timeout_seconds=5
    )

    assert container_running() is True