using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using VideoShortsGenerator.Application.Abstractions;
using VideoShortsGenerator.Domain.Enums;
using VideoShortsGenerator.Domain.Repositories;

namespace VideoShortsGenerator.Infrastructure.BackgroundServices;

public sealed class VideoProcessingWorker : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<VideoProcessingWorker> _logger;
    private readonly int _pollingIntervalSeconds;
    private readonly int _maxConcurrentJobs;

    public VideoProcessingWorker(
        IServiceProvider serviceProvider,
        ILogger<VideoProcessingWorker> logger,
        Microsoft.Extensions.Configuration.IConfiguration configuration)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;

        _pollingIntervalSeconds = configuration
            .GetValue<int>("BackgroundWorker:PollingIntervalSeconds", 5);

        _maxConcurrentJobs = configuration
            .GetValue<int>("BackgroundWorker:MaxConcurrentJobs", 1);
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation(
            "VideoProcessingWorker started. Polling every {Seconds}s, max {MaxJobs} concurrent jobs.",
            _pollingIntervalSeconds,
            _maxConcurrentJobs);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ProcessPendingJobsAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in VideoProcessingWorker. Worker will continue.");
            }

            await Task.Delay(
                TimeSpan.FromSeconds(_pollingIntervalSeconds),
                stoppingToken);
        }

        _logger.LogInformation("VideoProcessingWorker stopped.");
    }

    private async Task ProcessPendingJobsAsync(CancellationToken stoppingToken)
    {
        using var scope = _serviceProvider.CreateScope();

        var repository = scope.ServiceProvider.GetRequiredService<IVideoRepository>();
        var processor = scope.ServiceProvider.GetRequiredService<IVideoProcessor>();
        var storage = scope.ServiceProvider.GetRequiredService<IVideoStorage>();
        var dispatcher = scope.ServiceProvider.GetRequiredService<IEventDispatcher>();

        var pendingJobs = await repository.GetPendingAsync(stoppingToken);

        if (pendingJobs.Count == 0)
            return;

        _logger.LogInformation("Found {Count} pending jobs.", pendingJobs.Count);

        foreach (var job in pendingJobs)
        {
            if (stoppingToken.IsCancellationRequested)
                break;

            await ProcessSingleJobAsync(
                job.Id,
                repository,
                processor,
                storage,
                dispatcher,
                stoppingToken);
        }
    }

    private async Task ProcessSingleJobAsync(
        Guid jobId,
        IVideoRepository repository,
        IVideoProcessor processor,
        IVideoStorage storage,
        IEventDispatcher dispatcher,
        CancellationToken stoppingToken)
    {
        _logger.LogInformation("Starting processing for job {JobId}", jobId);

        try
        {
            var job = await repository.GetByIdAsync(jobId, stoppingToken);

            if (job is null)
            {
                _logger.LogWarning("Job {JobId} not found.", jobId);
                return;
            }

            if (job.Status != VideoStatus.Processing)
            {
                _logger.LogWarning(
                    "Job {JobId} is not in Processing status (current: {Status}). Skipping.",
                    jobId,
                    job.Status);
                return;
            }

            _logger.LogInformation("Processing video: {InputPath}", job.InputPath);

            var processedStream = await processor.ProcessAsync(job.InputPath, job.ProcessingType, job.Params, stoppingToken);

            _logger.LogInformation("Video processed successfully for job {JobId}. Saving...", jobId);

            var fileName = $"{job.Id}.mp4";
            var outputPath = await storage.SaveAsync(processedStream, fileName, stoppingToken);

            await processedStream.DisposeAsync();

            _logger.LogInformation("Video saved at {OutputPath} for job {JobId}", outputPath, jobId);

            job.MarkAsCompleted(outputPath);

            await repository.SaveChangesAsync(stoppingToken);

            await dispatcher.DispatchAsync(job.DomainEvents, stoppingToken);

            job.ClearDomainEvents();

            _logger.LogInformation("Job {JobId} completed successfully.", jobId);
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("Processing of job {JobId} was cancelled.", jobId);
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing job {JobId}: {Message}", jobId, ex.Message);

            try
            {
                var job = await repository.GetByIdAsync(jobId, stoppingToken);

                if (job is not null && job.Status == VideoStatus.Processing)
                {
                    job.MarkAsFailed();
                    await repository.SaveChangesAsync(stoppingToken);

                    await dispatcher.DispatchAsync(job.DomainEvents, stoppingToken);

                    job.ClearDomainEvents();

                    _logger.LogInformation("Job {JobId} marked as Failed.", jobId);
                }
            }
            catch (Exception innerEx)
            {
                _logger.LogError(innerEx, "Additional error marking job {JobId} as Failed.", jobId);
            }
        }
    }
}