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

    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    private VideoJob() { } // Es requerido por EF Core

    public VideoJob(string inputPath)
    {
        if (string.IsNullOrWhiteSpace(inputPath))
            throw new ArgumentException("InputPath no puede estar vacío", nameof(inputPath));

        Id = Guid.NewGuid();
        InputPath = inputPath;
        Status = VideoStatus.Pending;
        CreatedAt = DateTime.UtcNow;

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