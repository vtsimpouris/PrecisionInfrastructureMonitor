using System.Text.Json;
using PrecisionInfrastructureMonitor.Models;

namespace PrecisionInfrastructureMonitor.Services;

public class ConfigValidator
{
    private readonly string _rootPath;

    public ConfigValidator(string rootPath)
    {
        _rootPath = rootPath;
    }

    public bool IsValid()
    {
        string runtimePath =
            Path.Combine(_rootPath, "config", "runtime.json");

        if (!File.Exists(runtimePath))
            return false;

        string json = File.ReadAllText(runtimePath);

        RuntimeConfig? config =
            JsonSerializer.Deserialize<RuntimeConfig>(json);

        if (config == null)
            return false;

        string calibrationPath =
            Path.Combine(_rootPath, config.CalibrationPath);

        return File.Exists(calibrationPath);
    }
}