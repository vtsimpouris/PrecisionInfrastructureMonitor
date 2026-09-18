Feature: Service fault detection
  The monitoring system should detect intermittent service failures.

  Scenario: Measurement API returns an internal server error
    Given the monitoring service is healthy
    And a service failure is enabled
    When the measurement endpoint is probed
    Then an HTTP server error should be observed
    And the httpFailure residual should be active
    And the diagnosed fault should be service