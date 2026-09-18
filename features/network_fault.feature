Feature: Network fault detection
  The monitoring system should detect excessive communication delay.

  Scenario: Network delay exceeds the client timeout
    Given the monitoring service is healthy
    And a network delay greater than the request timeout is injected
    When the measurement endpoint is probed
    Then the measurement request should time out
    And the networkTimeout residual should be active
    And the diagnosed fault should be network