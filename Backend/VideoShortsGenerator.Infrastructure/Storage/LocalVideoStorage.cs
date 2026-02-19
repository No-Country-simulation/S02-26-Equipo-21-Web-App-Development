using Microsoft.Extensions.Configuration;
using VideoShortsGenerator.Application.Abstractions;

namespace VideoShortsGenerator.Infrastructure.Storage;

public sealed class LocalVideoStorage : IVideoStorage
{
    private readonly string _outputFolder;

    public LocalVideoStorage(IConfiguration configuration)
    {
        _outputFolder = configuration["VideoStorage:OutputFolder"]
            ?? Path.Combine(Directory.GetCurrentDirectory(), "Videos", "Outputs");

        Directory.CreateDirectory(_outputFolder);
    }

    public async Task<string> SaveAsync(
        Stream videoStream,
        string fileName,
        CancellationToken cancellationToken = default)
    {
        var outputPath = Path.Combine(_outputFolder, fileName);

        await using var fileStream = new FileStream(
            outputPath,
            FileMode.Create,
            FileAccess.Write,
            FileShare.None,
            bufferSize: 4096,
            useAsync: true);

        await videoStream.CopyToAsync(fileStream, cancellationToken);

        return outputPath;
    }

    public Task<bool> ExistsAsync(string filePath)
    {
        return Task.FromResult(File.Exists(filePath));
    }
}