using VideoShortsGenerator.Domain.Entities;

namespace VideoShortsGenerator.Domain.Repositories;

public interface IVideoRepository
{
    Task AddAsync(VideoJob job, CancellationToken cancellationToken = default);
    Task<VideoJob?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<List<VideoJob>> GetPendingAsync(CancellationToken cancellationToken = default);
    Task SaveChangesAsync(CancellationToken cancellationToken = default);
}
