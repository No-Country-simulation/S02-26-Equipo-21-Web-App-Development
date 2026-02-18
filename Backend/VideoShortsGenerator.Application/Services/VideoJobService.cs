using VideoShortsGenerator.Application.Abstractions;
using VideoShortsGenerator.Application.DTOs;
using VideoShortsGenerator.Domain.Entities;
using VideoShortsGenerator.Domain.Repositories;

namespace VideoShortsGenerator.Application.Services;

public sealed class VideoJobService
{
    private readonly IVideoRepository _repository;
    private readonly IEventDispatcher _dispatcher;
    private readonly IVideoStorage _storage;

    public VideoJobService(
        IVideoRepository repository,
        IEventDispatcher dispatcher,
        IVideoStorage storage)
    {
        _repository = repository;
        _dispatcher = dispatcher;
        _storage = storage;
    }

    public async Task<Guid> CreateAsync(
        CreateVideoJobRequest request,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(request.InputPath))
            throw new ArgumentException("InputPath cannot be empty.", nameof(request.InputPath));

        var exists = await _storage.ExistsAsync(request.InputPath);
        if (!exists)
            throw new FileNotFoundException($"File not found: {request.InputPath}");

        var job = new VideoJob(request.InputPath);

        await _repository.AddAsync(job, cancellationToken);
        await _repository.SaveChangesAsync(cancellationToken);

        await _dispatcher.DispatchAsync(job.DomainEvents, cancellationToken);

        job.ClearDomainEvents();

        return job.Id;
    }
}