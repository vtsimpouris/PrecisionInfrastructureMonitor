using PrecisionInfrastructureMonitor.Models;
using PrecisionInfrastructureMonitor.Services;

namespace PrecisionInfrastructureMonitor.Tests;

public class DiagnosticsServiceTests
{
    [Fact]
    public void Analyze_CalculatesMeanOffsetsCorrectly()
    {
        var measurements = new List<Measurement>
        {
            new() { XOffset = 0.01, YOffset = 0.02 },
            new() { XOffset = 0.03, YOffset = 0.04 }
        };

        var diagnostics = new DiagnosticsService();

        DiagnosticResult result =
            diagnostics.Analyze(measurements);

        Assert.InRange(
            result.MeanX,
            0.019999,
            0.020001);

        Assert.InRange(
            result.MeanY,
            0.029999,
            0.030001);
    }


    [Fact]
    public void Analyze_MarksSystemDegraded_WhenTooManyOutliers()
    {
        var measurements = new List<Measurement>
        {
            new() { XOffset = 0.0, YOffset = 0.0 },
            new() { XOffset = 0.0, YOffset = 0.0 },
            new() { XOffset = 0.0, YOffset = 0.0 },
            new() { XOffset = 0.10, YOffset = 0.10 }
        };

        var diagnostics = new DiagnosticsService();

        DiagnosticResult result =
            diagnostics.Analyze(measurements);

        Assert.Equal(1, result.OutlierCount);
        Assert.Equal("DEGRADED", result.Status);
    }
}