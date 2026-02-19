using VideoShortsGenerator.Application.DTOs;
using VideoShortsGenerator.Domain.Repositories;

namespace VideoShortsGenerator.Application.Services;

public sealed class VideoJobQueryService
{
    private readonly IVideoRepository _repository;

    public VideoJobQueryService(IVideoRepository repository)
    {
        _repository = repository;
    }

    public async Task<VideoJobResponse?> GetByIdAsync(
        Guid id,
        CancellationToken cancellationToken = default)
    {
        var job = await _repository.GetByIdAsync(id, cancellationToken);

        if (job is null)
            return null;

        return new VideoJobResponse
        {
            Id = job.Id,
            InputPath = job.InputPath,
            OutputPath = job.OutputPath,
            Status = job.Status.ToString(),
            CreatedAt = job.CreatedAt,
            CompletedAt = job.CompletedAt
        };
    }

    public async Task<List<VideoJobListResponse>> GetPendingAsync(
        CancellationToken cancellationToken = default)
    {
        var jobs = await _repository.GetPendingAsync(cancellationToken);

        return jobs.Select(job => new VideoJobListResponse
        {
            Id = job.Id,
            Status = job.Status.ToString(),
            CreatedAt = job.CreatedAt
        }).ToList();
    }

    public async Task<bool> ExistsAsync(
        Guid id,
        CancellationToken cancellationToken = default)
    {
        var job = await _repository.GetByIdAsync(id, cancellationToken);
        return job is not null;
    }
}