namespace PrecisionInfrastructureMonitor.Services;

public class FaultState
{
    public bool ServiceFailure { get; set; } = false;
    public int NetworkDelayMs { get; set; } = 0;
}