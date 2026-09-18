using PrecisionInfrastructureMonitor.Models;
namespace PrecisionInfrastructureMonitor.Services
{
    public class MeasurementSimulator
    {
        private readonly Random _random = new();

        public Measurement Generate()
        {
            return new Measurement
            {
                Timestamp = DateTime.UtcNow,

                XOffset = NextGaussian(0.0, 0.02),
                YOffset = NextGaussian(0.0, 0.02),

                Temperature = 35.0 +
                              _random.NextDouble(),

                Status = "OK"
            };
        }

        private double NextGaussian(
            double mean,
            double stdDev)
        {
            double u1 = 1.0 - _random.NextDouble();
            double u2 = 1.0 - _random.NextDouble();

            double randStdNormal =
                Math.Sqrt(-2.0 * Math.Log(u1)) *
                Math.Sin(2.0 * Math.PI * u2);

            return mean + stdDev * randStdNormal;
        }
    }
}
