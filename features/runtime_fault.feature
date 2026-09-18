Feature: Runtime fault detection
  The monitoring system should detect temporary container outages.

  Scenario: Service container becomes unavailable
    Given the monitoring service is healthy
    When the Docker container is stopped temporarily
    Then heartbeat loss should be observed
    And the HeartbeatLost residual should be active
    And the diagnosed fault should be runtime