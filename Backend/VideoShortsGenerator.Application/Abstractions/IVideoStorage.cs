namespace VideoShortsGenerator.Application.Abstractions;

public interface IVideoStorage
{
    Task<Stream> GetFileStreamAsync(string filePath);
    Task<string> SaveOriginalAsync(
    Stream videoStream,
    string originalFileName,
    CancellationToken cancellationToken = default);

    Task<string> SaveAsync(
        Stream videoStream,
        string fileName,
        CancellationToken cancellationToken = default);

    Task<bool> ExistsAsync(string filePath);
}