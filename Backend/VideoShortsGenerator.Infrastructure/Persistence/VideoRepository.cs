using Microsoft.EntityFrameworkCore;
using VideoShortsGenerator.Domain.Entities;
using VideoShortsGenerator.Domain.Enums;
using VideoShortsGenerator.Domain.Repositories;

namespace VideoShortsGenerator.Infrastructure.Persistence;

public sealed class VideoRepository : IVideoRepository
{
    private readonly ApplicationDbContext _context;

    public VideoRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task AddAsync(VideoJob job, CancellationToken cancellationToken = default)
    {
        await _context.VideoJobs.AddAsync(job, cancellationToken);
    }

    public async Task<VideoJob?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        return await _context.VideoJobs
            .FirstOrDefaultAsync(j => j.Id == id, cancellationToken);
    }

    public async Task<List<VideoJob>> GetPendingAsync(CancellationToken cancellationToken = default)
    {
        return await _context.VideoJobs
            .Where(j => j.Status == VideoStatus.Processing)
            .OrderBy(j => j.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        await _context.SaveChangesAsync(cancellationToken);
    }
}