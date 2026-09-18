import requests
import pytest

from pytest_bdd import scenario, given, when, then, parsers

from config import (
    BASE_URL,
    BAD_CALIBRATION_PATH,
    REQUEST_TIMEOUT,
)
from fault_injection import (
    reset_system,
    set_config,
    runtime_fault,
)
from probing import probe_system
from residuals import calculate_residuals, diagnose_fault


TEST_MATRIX = {
    "httpFailure": {
        "service": 1.0,
        "config": 1.0,
        "network": 1.0,
        "runtime": 1.0,
    },
    "configInvalid": {
        "service": 0.0,
        "config": 1.0,
        "network": 0.0,
        "runtime": 0.0,
    },
    "networkTimeout": {
        "service": 0.0,
        "config": 0.0,
        "network": 1.0,
        "runtime": 0.0,
    },
    "HeartbeatLost": {
        "service": 0.0,
        "config": 0.0,
        "network": 0.0,
        "runtime": 0.5,
    },
}


@scenario(
    "../features/service_fault.feature",
    "Measurement API returns an internal server error",
)
def test_service_fault():
    pass


@scenario(
    "../features/config_fault.feature",
    "Calibration configuration is invalid",
)
def test_config_fault():
    pass


@scenario(
    "../features/network_fault.feature",
    "Network delay exceeds the client timeout",
)
def test_network_fault():
    pass


@scenario(
    "../features/runtime_fault.feature",
    "Service container becomes unavailable",
)
def test_runtime_fault():
    pass


@pytest.fixture
def context():
    reset_system()

    data = {}

    yield data

    reset_system()


@given("the monitoring service is healthy")
def monitoring_service_is_healthy(context):
    reset_system()


@given("a service failure is enabled")
def service_failure_enabled(context):

    requests.post(
        f"{BASE_URL}/faults/service/true",
        timeout=REQUEST_TIMEOUT,
    ).raise_for_status()

    context["fault"] = "service"


@given("an invalid calibration path is configured")
def invalid_configuration(context):

    set_config(BAD_CALIBRATION_PATH)

    context["fault"] = "config"


@given(
    "a network delay greater than the request timeout is injected"
)
def network_delay_injected(context):

    delay_ms = int(
        (REQUEST_TIMEOUT + 0.25) * 1000
    )

    requests.post(
        f"{BASE_URL}/faults/network/{delay_ms}",
        timeout=REQUEST_TIMEOUT,
    ).raise_for_status()

    context["fault"] = "network"


@when("the measurement endpoint is probed")
def measurement_endpoint_probed(context):

    if context["fault"] == "service":

        # Service failure is intentionally intermittent.
        # Retry until the injected HTTP 500 is observed.
        for _ in range(10):

            observation = probe_system()

            if (
                observation["httpOutcome"]
                == "server_error"
            ):
                break

    else:
        observation = probe_system()

    context["observation"] = observation
    context["residuals"] = (
        calculate_residuals(observation)
    )


@when("the system configuration is probed")
def configuration_is_probed(context):

    observation = probe_system()

    context["observation"] = observation
    context["residuals"] = (
        calculate_residuals(observation)
    )


@when("the Docker container is stopped temporarily")
def docker_container_stopped(context):

    observation = runtime_fault()

    context["fault"] = "runtime"
    context["observation"] = observation
    context["residuals"] = (
        calculate_residuals(observation)
    )


@then("an HTTP server error should be observed")
def http_server_error_observed(context):

    assert (
        context["observation"]["httpOutcome"]
        == "server_error"
    )


@then("the configuration should be reported as invalid")
def configuration_reported_invalid(context):

    assert (
        context["observation"]["configValid"]
        is False
    )


@then("the measurement request should time out")
def measurement_request_times_out(context):

    assert (
        context["observation"]["httpOutcome"]
        == "timeout"
    )


@then("heartbeat loss should be observed")
def heartbeat_loss_observed(context):

    assert (
        context["observation"]
        .get("heartbeatLossRate", 0)
        > 0
    )


@then(
    parsers.parse(
        "the {residual_name} residual should be active"
    )
)
def residual_should_be_active(
    context,
    residual_name,
):

    assert (
        context["residuals"][residual_name]
        > 0
    )


@then(
    parsers.parse(
        "the diagnosed fault should be {expected_fault}"
    )
)
def diagnosed_fault_should_be(
    context,
    expected_fault,
):

    predicted_fault, _ = diagnose_fault(
        context["residuals"],
        TEST_MATRIX,
    )

    assert predicted_fault == expected_fault