namespace VideoShortsGenerator.Application.Abstractions;

public interface IVideoStorage
{
    Task<string> SaveAsync(
        Stream videoStream,
        string fileName,
        CancellationToken cancellationToken = default);

    Task<bool> ExistsAsync(string filePath);
}