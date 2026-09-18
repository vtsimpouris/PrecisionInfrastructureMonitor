from residuals import (
    calculate_residuals,
    diagnose_fault
)


TEST_MATRIX = {
    "httpFailure": {
        "service": 0.85,
        "config": 1.00,
        "network": 0.55,
        "runtime": 1.00
    },
    "configInvalid": {
        "service": 0.00,
        "config": 1.00,
        "network": 0.00,
        "runtime": 0.00
    },
    "networkTimeout": {
        "service": 0.00,
        "config": 0.00,
        "network": 0.55,
        "runtime": 0.00
    },
    "HeartbeatLost": {
        "service": 0.00,
        "config": 0.00,
        "network": 0.00,
        "runtime": 0.54
    }
}


def test_calculate_residuals_healthy():

    observation = {
        "heartbeat": True,
        "configValid": True,
        "httpStatus": 200,
        "httpOutcome": "ok"
    }

    residuals = calculate_residuals(observation)

    assert residuals == {
        "httpFailure": 0,
        "configInvalid": 0,
        "networkTimeout": 0,
        "HeartbeatLost": 0.0
    }


def test_calculate_residuals_network_timeout():

    observation = {
        "heartbeat": True,
        "configValid": True,
        "httpStatus": None,
        "httpOutcome": "timeout"
    }

    residuals = calculate_residuals(observation)

    assert residuals["httpFailure"] == 1
    assert residuals["networkTimeout"] == 1
    assert residuals["configInvalid"] == 0
    assert residuals["HeartbeatLost"] == 0.0


def test_diagnose_network_fault():

    residuals = {
        "httpFailure": 1,
        "configInvalid": 0,
        "networkTimeout": 1,
        "HeartbeatLost": 0
    }

    fault, distance = diagnose_fault(
        residuals,
        TEST_MATRIX
    )

    assert fault == "network"
    assert distance >= 0


def test_diagnose_config_fault():

    residuals = {
        "httpFailure": 1,
        "configInvalid": 1,
        "networkTimeout": 0,
        "HeartbeatLost": 0
    }

    fault, distance = diagnose_fault(
        residuals,
        TEST_MATRIX
    )

    assert fault == "config"
    assert distance == 0


def test_diagnose_runtime_fault():

    residuals = {
        "httpFailure": 1,
        "configInvalid": 0,
        "networkTimeout": 0,
        "HeartbeatLost": 1
    }

    fault, distance = diagnose_fault(
        residuals,
        TEST_MATRIX
    )

    assert fault == "runtime"
    assert distance >= 0


def test_diagnose_healthy():

    residuals = {
        "httpFailure": 0,
        "configInvalid": 0,
        "networkTimeout": 0,
        "HeartbeatLost": 0
    }

    fault, distance = diagnose_fault(
        residuals,
        TEST_MATRIX
    )

    assert fault == "healthy"
    assert distance == 0