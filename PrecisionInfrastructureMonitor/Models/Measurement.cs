namespace PrecisionInfrastructureMonitor.Models
{
    public class Measurement
    {
        public DateTime Timestamp { get; set; }

        public double XOffset { get; set; }
        public double YOffset { get; set; }

        public double Temperature { get; set; }

        public string Status { get; set; } = "OK";
    }
}
