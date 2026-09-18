# Precision Infrastructure Monitor

[![CI](https://github.com/vtsimpouris/PrecisionInfrastructureMonitor/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/vtsimpouris/PrecisionInfrastructureMonitor/actions/workflows/ci.yml)

Automated system-integration testing and fault-diagnosis platform for a Dockerized C# / ASP.NET Core service.

The project combines **C#/.NET**, **Docker**, **Python test automation**, **Gherkin/BDD scenarios**, fault injection, residual-based diagnostics, and **GitHub Actions CI**. Its purpose is to demonstrate how faults can be injected, observed, classified, and validated across several system layers.

> The ASP.NET Core application is a simulated system under test. The main focus is the automated test and diagnostic infrastructure around it.

---

## What this project demonstrates

- Dockerized ASP.NET Core system under test
- Controlled **service, configuration, network, and runtime faults**
- Python orchestration for fault injection and system probing
- Docker lifecycle control during runtime-fault tests
- Residual generation from observable system behaviour
- Empirical **sensitivity-matrix estimation**
- Distance-based fault classification
- Validation-derived class thresholds
- **Unknown-fault rejection**
- Executable **Gherkin / pytest-bdd** scenarios
- C# unit tests, Python unit tests, and Docker-backed integration tests
- Automated clean-environment validation with **GitHub Actions**

---

## Architecture

The project follows a simple test-and-diagnose pipeline:

```text
┌───────────────────────────────┐
│ Python / Gherkin Test Runner  │
│                               │
│ • Inject faults               │
│ • Probe the system            │
│ • Control Docker              │
└───────────────┬───────────────┘
                │
                │ HTTP / config / container control
                ▼
┌───────────────────────────────┐
│ Dockerized ASP.NET Core SUT   │
│                               │
│ • Measurement API             │
│ • Runtime configuration       │
│ • Injected fault state        │
└───────────────┬───────────────┘
                │
                │ observations
                ▼
┌───────────────────────────────┐
│ Residual Vector               │
│                               │
│ • HTTP failure                │
│ • Config invalid              │
│ • Network timeout             │
│ • Heartbeat loss              │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Empirical Sensitivity Matrix  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Fault Diagnosis               │
│                               │
│ SERVICE / CONFIG / NETWORK    │
│ RUNTIME / UNKNOWN             │
└───────────────────────────────┘
```

Python drives the experiment by injecting faults into the Dockerized C# service and observing the resulting behaviour. Those observations are converted into residuals, which are used to estimate fault signatures in the sensitivity matrix and diagnose subsequent observations.

---

## Fault model

| Fault | Injection mechanism | Typical observable effect |
|---|---|---|
| `service` | Enables intermittent service failure behaviour | HTTP 500 responses |
| `config` | Replaces the valid calibration path with an invalid one | Configuration validation failure / HTTP 500 |
| `network` | Adds artificial response delay | Client request timeout |
| `runtime` | Temporarily stops the Docker container | Heartbeat loss / service unavailable |

The service fault is intentionally intermittent, while network delay and runtime downtime also contain randomized behaviour. This avoids reducing the experiment to fixed one-to-one mappings.

---

## Residuals

Each observation is converted into four diagnostic residuals:

| Residual | Meaning |
|---|---|
| `httpFailure` | The measurement endpoint did not return HTTP 200 |
| `configInvalid` | Runtime configuration failed validation |
| `networkTimeout` | The measurement request exceeded the client timeout |
| `HeartbeatLost` | Fraction of heartbeat checks lost during the observation window |

The residual vector is therefore:

```text
r = [httpFailure, configInvalid, networkTimeout, HeartbeatLost]
```

---

## Sensitivity matrix

The sensitivity matrix is estimated empirically by repeatedly injecting each known fault and averaging the resulting residual responses.

Conceptually:

```text
S[i,j] = average response of residual i when fault j is injected
```

A recent run produced:

```text
Sensitivity Matrix S

Residual              service     config      network     runtime
----------------------------------------------------------------------
httpFailure           0.85        1.00        0.60        1.00
configInvalid         0.00        1.00        0.00        0.00
networkTimeout        0.00        0.00        0.60        0.00
HeartbeatLost         0.00        0.00        0.00        0.54
```

Each matrix column represents the empirical residual signature of one known fault class.

Because the injected faults are intentionally stochastic, exact matrix values vary between runs.

---

## Fault diagnosis

For a new observation, the measured residual vector is compared with each known fault signature using Euclidean distance.

```text
predicted class = fault signature with the minimum distance
```

Blind validation is then used to derive a class-specific acceptance threshold. The current implementation uses the **95th percentile of correctly classified validation distances** for each known fault.

A classification is accepted only when:

```text
minimum distance <= threshold for the nearest class
```

Otherwise the result is:

```text
UNKNOWN
```

This prevents arbitrary residual patterns from always being forced into one of the known classes.

---

## Representative diagnostic run

The following is output from a recent local run:

```text
Injecting HEALTHY  [20 runs]... done
Injecting SERVICE  [20 runs]... done
Injecting CONFIG   [20 runs]... done
Injecting NETWORK  [20 runs]... done
Injecting RUNTIME  [20 runs]... done

Experiment results: ...\experiment_results.json
Sensitivity matrix: ...\sensitivity_matrix.json

Running blind validation [100 runs]... done

Sensitivity Matrix S

Residual              service     config      network     runtime
----------------------------------------------------------------------
httpFailure           0.85        1.00        0.60        1.00
configInvalid         0.00        1.00        0.00        0.00
networkTimeout        0.00        0.00        0.60        0.00
HeartbeatLost         0.00        0.00        0.00        0.54

Distance thresholds
service    0.15
config     0.00
network    0.57
runtime    0.24

Confusion Matrix

Actual      service     config      network     runtime     healthy
------------------------------------------------------------------------
service     19          0           0           0           4
config      0           18          0           0           0
network     0           0           12          0           12
runtime     0           0           0           35          0

Diagnostic accuracy: 84.0%
```

The 100-run blind validation is intentionally small enough to keep the demonstration quick. A production study would use a larger and more systematically stratified validation dataset.

### Unseen residual combination

The diagnostic layer can evaluate a residual combination that is not itself one of the learned signatures:

```text
Unseen residual vector:
{'httpFailure': 1, 'configInvalid': 0, 'networkTimeout': 1, 'HeartbeatLost': 0}

Nearest known class: NETWORK
Distance from signature: 0.57
Acceptance threshold: 0.57
Diagnosis: NETWORK
```

### Novel-pattern rejection

A sufficiently different residual pattern is rejected instead of being forced into the nearest known class:

```text
Novel residual vector:
{'httpFailure': 0, 'configInvalid': 1, 'networkTimeout': 1, 'HeartbeatLost': 1}

Nearest known class: NETWORK
Distance from signature: 1.59
Acceptance threshold: 0.57
Diagnosis: UNKNOWN
```

---

## Automated tests

The repository contains several complementary test layers.

### C# unit tests

The C# test project validates components such as:

- valid runtime configuration
- missing/invalid calibration configuration
- diagnostic statistics
- degraded-state detection from simulated measurements

### Python unit tests

Deterministic Python tests validate the residual and diagnosis logic independently of HTTP and Docker behaviour.

### Docker-backed integration tests

The integration tests run against the actual containerized service and verify:

- healthy API and configuration behaviour
- intermittent service failures
- invalid runtime configuration
- network timeout injection
- container outage and recovery

### Executable Gherkin scenarios

Human-readable behaviour specifications are stored in `features/` and executed through `pytest-bdd`.

Example:

```gherkin
Feature: Runtime fault detection
  The monitoring system should detect temporary container outages.

  Scenario: Service container becomes unavailable
    Given the monitoring service is healthy
    When the Docker container is stopped temporarily
    Then heartbeat loss should be observed
    And the HeartbeatLost residual should be active
    And the diagnosed fault should be runtime
```

The Gherkin files are executable system tests rather than documentation-only scenarios.

---

## Continuous Integration

GitHub Actions validates the repository on a clean runner after pushes and pull requests.

The workflow contains two main jobs:

```text
Build and Unit Tests
├── Build ASP.NET Core project
├── Run C# unit tests
└── Run Python unit tests

Docker System Tests
├── Build Docker image
├── Start the system under test
├── Run executable Gherkin scenarios
└── Run Docker-backed integration tests
```

The CI badge at the top of this README reflects the current workflow status on the `main` branch.

A passing workflow therefore verifies that the project builds and its automated test layers run successfully outside the local development environment.

---

## How to run

### Prerequisites

- Git
- Docker Desktop, or Docker Engine with Compose support
- Python 3

For the normal end-to-end path, the C# service is built inside Docker, so a local .NET SDK is not required.

### 1. Clone the repository

```bash
git clone https://github.com/vtsimpouris/PrecisionInfrastructureMonitor.git
cd PrecisionInfrastructureMonitor
```

### 2. Start the system under test

```bash
docker compose up -d --build
```

This builds the ASP.NET Core image, starts the service as `precision-monitor`, exposes it on port `7060`, and mounts the runtime configuration directory.

### 3. Create the Python environment

From the repository root:

```bash
cd scripts
python -m venv .venv
```

#### Windows PowerShell

Install dependencies without requiring virtual-environment activation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the diagnostic experiment:

```powershell
.\.venv\Scripts\python.exe .\main.py
```

Verbose mode:

```powershell
.\.venv\Scripts\python.exe .\main.py -v
```

#### Linux / macOS

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Verbose mode:

```bash
.venv/bin/python main.py -v
```

### 4. Run the Python test suites

From `scripts/`:

#### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Individual layers:

```powershell
.\.venv\Scripts\python.exe -m pytest -q test_residuals.py
.\.venv\Scripts\python.exe -m pytest -q test_integration.py
.\.venv\Scripts\python.exe -m pytest -q test_bdd.py
```

#### Linux / macOS

```bash
.venv/bin/python -m pytest -q
```

### 5. Run the C# unit tests separately

If the .NET SDK is installed locally:

```bash
dotnet test PrecisionInfrastructureMonitor.Tests/PrecisionInfrastructureMonitor.Tests.csproj
```

Run this command from the repository root.

### 6. Stop the environment

From the repository root:

```bash
docker compose down
```

---

## Project structure

```text
PrecisionInfrastructureMonitor/
├── .github/
│   └── workflows/
│       └── ci.yml
├── features/
│   ├── service_fault.feature
│   ├── config_fault.feature
│   ├── network_fault.feature
│   └── runtime_fault.feature
├── scripts/
│   ├── main.py
│   ├── config.py
│   ├── docker_utils.py
│   ├── fault_injection.py
│   ├── probing.py
│   ├── residuals.py
│   ├── experiments.py
│   ├── validation.py
│   ├── test_residuals.py
│   ├── test_integration.py
│   ├── test_bdd.py
│   └── requirements.txt
├── PrecisionInfrastructureMonitor/
│   ├── Program.cs
│   ├── Dockerfile
│   ├── config/
│   │   ├── runtime.json
│   │   └── calibration.json
│   ├── Models/
│   └── Services/
├── PrecisionInfrastructureMonitor.Tests/
├── docker-compose.yml
├── PrecisionInfrastructureMonitor.slnx
└── README.md
```

---

## Design intent

The project is intentionally compact enough to inspect end-to-end while still demonstrating a complete automated system-test workflow:

```text
deployment
    ↓
fault injection
    ↓
system observation
    ↓
residual generation
    ↓
sensitivity-matrix estimation
    ↓
fault diagnosis
    ↓
blind validation
    ↓
unknown-fault rejection
    ↓
continuous integration
```

It is not intended to reproduce every detail of a production industrial control system. Instead, it provides a reproducible platform for experimenting with **system integration testing, controlled failure injection, failure isolation, diagnostic signatures, and CI-backed test automation** across application and container boundaries.
