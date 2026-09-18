from pathlib import Path

BASE_URL = "http://localhost:7060"
CONTAINER_NAME = "precision-monitor"

REPO_ROOT = Path(__file__).resolve().parents[1]

SERVICE_ROOT = (
    REPO_ROOT
    / "PrecisionInfrastructureMonitor"
)

RUNTIME_CONFIG_PATH = (
    SERVICE_ROOT
    / "config"
    / "runtime.json"
)

GOOD_CALIBRATION_PATH = "config/calibration.json"
BAD_CALIBRATION_PATH = "config/DOES_NOT_EXIST.json"

REQUEST_TIMEOUT = 1.0
RUNS_PER_FAULT = 20