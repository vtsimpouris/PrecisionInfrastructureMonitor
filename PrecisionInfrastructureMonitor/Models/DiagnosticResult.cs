namespace PrecisionInfrastructureMonitor.Models;

public class DiagnosticResult
{
    public int SampleCount { get; set; }

    public double MeanX { get; set; }
    public double MeanY { get; set; }

    public double StdDevX { get; set; }
    public double StdDevY { get; set; }

    public double MeanRadialError { get; set; }

    public int OutlierCount { get; set; }
    public double OutlierPercentage { get; set; }

    public string Status { get; set; } = "OK";
}