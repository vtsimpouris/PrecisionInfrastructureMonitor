Feature: Configuration fault detection
  The monitoring system should detect invalid runtime configuration.

  Scenario: Calibration configuration is invalid
    Given the monitoring service is healthy
    And an invalid calibration path is configured
    When the system configuration is probed
    Then the configuration should be reported as invalid
    And the configInvalid residual should be active
    And the diagnosed fault should be config