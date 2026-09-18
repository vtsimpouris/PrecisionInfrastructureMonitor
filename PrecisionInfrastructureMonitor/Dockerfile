FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY ["PrecisionInfrastructureMonitor.csproj", "./"]
RUN dotnet restore "PrecisionInfrastructureMonitor.csproj"

COPY . .
RUN dotnet publish "PrecisionInfrastructureMonitor.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app

COPY --from=build /app/publish .
COPY config ./config

EXPOSE 8080

ENTRYPOINT ["dotnet", "PrecisionInfrastructureMonitor.dll"]