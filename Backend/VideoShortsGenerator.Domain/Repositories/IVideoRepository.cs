using System;
using VideoShortsGenerator.Domain.Entities;

namespace VideoShortsGenerator.Domain.Repositories;

public interface IVideoRepository
{
    Task AddAsync(VideoJob job);
    Task<VideoJob?> GetByIdAsync(Guid id);
    Task<List<VideoJob>> GetPendingAsync();
    Task SaveChangesAsync();
}
