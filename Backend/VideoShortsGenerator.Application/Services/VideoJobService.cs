using VideoShortsGenerator.Application.Abstractions;
using VideoShortsGenerator.Domain.Entities;
using VideoShortsGenerator.Domain.Enums;
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
    public async Task<Guid> VideoUploadAsync(Stream stream, string fileName, CancellationToken ct)
    {
        var extension = Path.GetExtension(fileName).ToLower();

        // 1. Mandamos a guardar físicamente
        string inputPath = await _storage.SaveOriginalAsync(stream, extension, ct);
        // 2. Creamos el job en la base de datos
        Guid id = await CreateAsync(inputPath, ct);
        return id;
    }

    public async Task<Guid> CreateAsync(
        string inputPath,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(inputPath))
            throw new ArgumentException("InputPath cannot be empty.", nameof(inputPath));

        var exists = await _storage.ExistsAsync(inputPath);
        if (!exists)
            throw new FileNotFoundException($"File not found: {inputPath}");

        var job = new VideoJob(inputPath);

        await _repository.AddAsync(job, cancellationToken);
        await _repository.SaveChangesAsync(cancellationToken);

        await _dispatcher.DispatchAsync(job.DomainEvents, cancellationToken);

        job.ClearDomainEvents();

        return job.Id;
    }

    public async Task<(Stream stream, string fileName)> GetVideoDownloadAsync(Guid id, CancellationToken ct)
    {
        var job = await _repository.GetByIdAsync(id, ct);

        // El servicio toma decisiones de negocio
        if (job == null || job.Status != VideoStatus.Completed)
            return (null, null);

        // El servicio le pide el "bruto" al storage
        var stream = await _storage.GetFileStreamAsync(job.OutputPath);

        return (stream, $"video_{id}.mp4");
    }
}