using PrecisionInfrastructureMonitor.Models;

namespace PrecisionInfrastructureMonitor.Services;

public class DiagnosticsService
{
    public DiagnosticResult Analyze(List<Measurement> measurements)
    {
        double meanX = measurements.Average(m => m.XOffset);
        double meanY = measurements.Average(m => m.YOffset);

        double varianceX =
            measurements.Average(m =>
                Math.Pow(m.XOffset - meanX, 2));

        double varianceY =
            measurements.Average(m =>
                Math.Pow(m.YOffset - meanY, 2));

        double stdDevX = Math.Sqrt(varianceX);
        double stdDevY = Math.Sqrt(varianceY);

        double meanRadialError =
            measurements.Average(m =>
                Math.Sqrt(
                    m.XOffset * m.XOffset +
                    m.YOffset * m.YOffset));

        const double outlierThreshold = 0.05;

        int outliers = measurements.Count(m =>
            Math.Sqrt(
                m.XOffset * m.XOffset +
                m.YOffset * m.YOffset)
            > outlierThreshold);

        double outlierPercentage =
            100.0 * outliers / measurements.Count;

        return new DiagnosticResult
        {
            SampleCount = measurements.Count,

            MeanX = meanX,
            MeanY = meanY,

            StdDevX = stdDevX,
            StdDevY = stdDevY,

            MeanRadialError = meanRadialError,

            OutlierCount = outliers,
            OutlierPercentage = outlierPercentage,

            Status = outlierPercentage > 10.0
                ? "DEGRADED"
                : "OK"
        };
    }
}