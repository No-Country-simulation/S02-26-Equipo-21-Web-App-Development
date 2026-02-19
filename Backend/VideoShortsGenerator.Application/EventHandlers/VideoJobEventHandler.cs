using VideoShortsGenerator.Application.Abstractions;
using VideoShortsGenerator.Domain.Events;
using VideoShortsGenerator.Domain.Repositories;

namespace VideoShortsGenerator.Application.EventHandlers;

public sealed class VideoJobEventHandler
{
    private readonly IVideoRepository _repository;
    private readonly IEventDispatcher _dispatcher;

    public VideoJobEventHandler(
        IVideoRepository repository,
        IEventDispatcher dispatcher)
    {
        _repository = repository;
        _dispatcher = dispatcher;
    }

    public async Task HandleAsync(
        VideoCreatedEvent domainEvent,
        CancellationToken cancellationToken = default)
    {
        var job = await _repository.GetByIdAsync(domainEvent.VideoId, cancellationToken);

        if (job is null)
            return;

        job.MarkAsProcessing();

        await _repository.SaveChangesAsync(cancellationToken);

        job.ClearDomainEvents();
    }

    public async Task HandleAsync(
        VideoCompletedEvent domainEvent,
        CancellationToken cancellationToken = default)
    {
        await Task.CompletedTask;
    }

    public async Task HandleAsync(
        VideoFailedEvent domainEvent,
        CancellationToken cancellationToken = default)
    {
        await Task.CompletedTask;
    }
}