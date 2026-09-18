using PrecisionInfrastructureMonitor.Models;
using PrecisionInfrastructureMonitor.Services;
var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();
builder.Logging.ClearProviders();
builder.Logging.AddConsole();

builder.Logging.AddFilter(
    "Microsoft",
    LogLevel.Warning
);

builder.Logging.AddFilter(
    "System",
    LogLevel.Warning
);
var app = builder.Build();
var logger = app.Logger;

var configValidator =
    new ConfigValidator(app.Environment.ContentRootPath);


// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

//app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

var simulator = new PrecisionInfrastructureMonitor.Services.MeasurementSimulator();

var faultState = new FaultState();

app.MapGet("/config/health", () =>
{
    bool valid = configValidator.IsValid();

    if (!valid)
    {
        logger.LogInformation(
            "Configuration health check failed"
        );
    }

    return new
    {
        valid
    };
});

app.MapGet("/measurements", async () =>
{
    if (faultState.ServiceFailure)
    {
        const double failureProbability = 0.85;

        if (
            Random.Shared.NextDouble()
            < failureProbability
        )
        {
            logger.LogInformation(
                "Injected service failure: returning HTTP 500"
            );

            return Results.StatusCode(500);
        }
    }

    if (!configValidator.IsValid())
    {
        logger.LogInformation(
            "Invalid configuration: returning HTTP 500"
        );

        return Results.StatusCode(500);
    }

    if (faultState.NetworkDelayMs > 0)
    {
        logger.LogInformation(
            "Applying network delay: {DelayMs} ms",
            faultState.NetworkDelayMs
        );

        await Task.Delay(
            faultState.NetworkDelayMs
        );
    }

    var measurement = simulator.Generate();

    logger.LogDebug(
        "Measurement generated successfully"
    );

    return Results.Ok(measurement);
});

app.MapGet("/measurements/batch/{count:int}", (int count) =>
{
    count = Math.Clamp(count, 1, 1000);

    var measurements = new List<Measurement>();

    for (int i = 0; i < count; i++)
    {
        measurements.Add(simulator.Generate());
    }

    return measurements;
});

var diagnostics =
    new PrecisionInfrastructureMonitor.Services.DiagnosticsService();
app.MapGet("/diagnostics/{count:int}", (int count) =>
{
    count = Math.Clamp(count, 1, 1000);

    var measurements = new List<Measurement>();

    for (int i = 0; i < count; i++)
    {
        measurements.Add(simulator.Generate());
    }

    return diagnostics.Analyze(measurements);
});
// Faulty endpoints
app.MapPost("/faults/service/{enabled:bool}", (bool enabled) =>
{
    faultState.ServiceFailure = enabled;

    logger.LogInformation(
        "Service fault set to {Enabled}",
        enabled
    );

    return Results.Ok(new
    {
        serviceFailure = enabled
    });
});


app.MapPost("/faults/network/{delayMs:int}", (int delayMs) =>
{
    faultState.NetworkDelayMs = Math.Max(
        0,
        delayMs
    );

    logger.LogInformation(
        "Network delay set to {DelayMs} ms",
        faultState.NetworkDelayMs
    );

    return Results.Ok(new
    {
        networkDelayMs =
            faultState.NetworkDelayMs
    });
});


app.MapPost("/faults/reset", () =>
{
    faultState.ServiceFailure = false;
    faultState.NetworkDelayMs = 0;

    logger.LogInformation(
        "Fault state reset"
    );

    return Results.Ok(new
    {
        status = "Healthy"
    });
});

app.Run();
