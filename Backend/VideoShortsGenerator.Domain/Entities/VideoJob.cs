    using System.Text.Json;
using VideoShortsGenerator.Domain.Enums;
using VideoShortsGenerator.Domain.Events;

namespace VideoShortsGenerator.Domain.Entities;

public sealed class VideoJob
{
    private readonly List<IDomainEvent> _domainEvents = new();

    public Guid Id { get; private set; }
    public string InputPath { get; private set; }
    public string? OutputPath { get; private set; }
    public VideoStatus Status { get; private set; }
    public DateTime CreatedAt { get; private set; }
    public DateTime? CompletedAt { get; private set; }

    // Nuevo: JSON de parámetros arbitrarios
    public string Params { get; private set; } = "{}";

    // Nuevo: tipo de procesamiento decidido (mapeado desde Params si se provee)
    public ProcessingType ProcessingType { get; private set; } = ProcessingType.Simple;

    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    private VideoJob() { } // Es requerido por EF Core

    // Constructor existente (mantengo compatibilidad)
    public VideoJob(string inputPath) : this(inputPath, "{}") { }

    // Nuevo constructor que acepta params JSON
    public VideoJob(string inputPath, string paramsJson)
    {
        if (string.IsNullOrWhiteSpace(inputPath))
            throw new ArgumentException("InputPath no puede estar vacío", nameof(inputPath));

        Id = Guid.NewGuid();
        InputPath = inputPath;
        Status = VideoStatus.Pending;
        CreatedAt = DateTime.UtcNow;

        Params = string.IsNullOrWhiteSpace(paramsJson) ? "{}" : paramsJson;

        // Intentar extraer el tipo de procesamiento desde el JSON:
        try
        {
            using var doc = JsonDocument.Parse(Params);
            if (doc.RootElement.TryGetProperty("processType", out var p) && p.ValueKind == JsonValueKind.String)
            {
                var s = p.GetString()!.ToLowerInvariant();
                ProcessingType = s switch
                {
                    "advanced" => ProcessingType.Advanced,
                    _ => ProcessingType.Simple
                };
            }
            else if (doc.RootElement.TryGetProperty("contentType", out var c) && c.ValueKind == JsonValueKind.String)
            {
                var s2 = c.GetString()!.ToLowerInvariant();
                ProcessingType = s2 switch
                {
                    "advanced" => ProcessingType.Advanced,
                    _ => ProcessingType.Simple
                };
            }
        }
        catch
        {
            // Ignore parse errors, dejamos valores por defecto
            ProcessingType = ProcessingType.Simple;
        }

        AddDomainEvent(new VideoCreatedEvent(Id));
    }

    public void MarkAsProcessing()
    {
        if (Status != VideoStatus.Pending)
            throw new InvalidOperationException($"No se puede iniciar el procesamiento. Estado actual: {Status}");

        Status = VideoStatus.Processing;
        AddDomainEvent(new VideoProcessingStartedEvent(Id));
    }

    public void MarkAsCompleted(string outputPath)
    {
        if (Status != VideoStatus.Processing)
            throw new InvalidOperationException($"No se puede completar. Estado actual: {Status}");

        if (string.IsNullOrWhiteSpace(outputPath))
            throw new ArgumentException("OutputPath no puede estar vacío", nameof(outputPath));

        Status = VideoStatus.Completed;
        OutputPath = outputPath;
        CompletedAt = DateTime.UtcNow;

        AddDomainEvent(new VideoCompletedEvent(Id, outputPath));
    }

    public void MarkAsFailed()
    {
        if (Status != VideoStatus.Processing)
            throw new InvalidOperationException($"No se puede marcar como fallido. Estado actual: {Status}");

        Status = VideoStatus.Failed;
        CompletedAt = DateTime.UtcNow;

        AddDomainEvent(new VideoFailedEvent(Id));
    }

    private void AddDomainEvent(IDomainEvent domainEvent)
    {
        _domainEvents.Add(domainEvent);
    }

    public void ClearDomainEvents()
    {
        _domainEvents.Clear();
    }
}