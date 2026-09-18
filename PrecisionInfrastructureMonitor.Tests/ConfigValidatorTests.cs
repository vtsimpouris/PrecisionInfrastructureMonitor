using PrecisionInfrastructureMonitor.Services;

namespace PrecisionInfrastructureMonitor.Tests;

public class ConfigValidatorTests
{
    [Fact]
    public void IsValid_ReturnsTrue_WhenCalibrationFileExists()
    {
        string root = CreateTestDirectory();

        try
        {
            string configDirectory =
                Path.Combine(root, "config");

            Directory.CreateDirectory(configDirectory);

            File.WriteAllText(
                Path.Combine(configDirectory, "calibration.json"),
                "{}");

            File.WriteAllText(
                Path.Combine(configDirectory, "runtime.json"),
                """
                {
                    "CalibrationPath": "config/calibration.json"
                }
                """);

            var validator = new ConfigValidator(root);

            Assert.True(validator.IsValid());
        }
        finally
        {
            Directory.Delete(root, true);
        }
    }


    [Fact]
    public void IsValid_ReturnsFalse_WhenCalibrationFileMissing()
    {
        string root = CreateTestDirectory();

        try
        {
            string configDirectory =
                Path.Combine(root, "config");

            Directory.CreateDirectory(configDirectory);

            File.WriteAllText(
                Path.Combine(configDirectory, "runtime.json"),
                """
                {
                    "CalibrationPath": "config/missing.json"
                }
                """);

            var validator = new ConfigValidator(root);

            Assert.False(validator.IsValid());
        }
        finally
        {
            Directory.Delete(root, true);
        }
    }


    private static string CreateTestDirectory()
    {
        string path = Path.Combine(
            Path.GetTempPath(),
            Guid.NewGuid().ToString());

        Directory.CreateDirectory(path);

        return path;
    }
}