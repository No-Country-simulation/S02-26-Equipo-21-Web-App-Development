namespace VideoShortsGenerator.Application.Abstractions;

public interface IVideoProcessor
{
    Task<Stream> ProcessAsync(
        string inputPath,
        CancellationToken cancellationToken = default);
}