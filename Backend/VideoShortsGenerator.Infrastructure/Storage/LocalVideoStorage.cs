using Microsoft.Extensions.Configuration;
using VideoShortsGenerator.Application.Abstractions;

namespace VideoShortsGenerator.Infrastructure.Storage;

public sealed class LocalVideoStorage : IVideoStorage
{
    private readonly string _outputFolder;
    private readonly string _originalsFolder;

    public LocalVideoStorage(IConfiguration configuration)
    {
        _outputFolder = configuration["VideoStorage:OutputFolder"]
            ?? Path.Combine(Directory.GetCurrentDirectory(), "Videos", "Outputs");

        _originalsFolder = configuration["VideoStorage:OriginalsFolder"]
            ?? Path.Combine(Directory.GetCurrentDirectory(), "storage", "originales");

        Directory.CreateDirectory(_outputFolder);
    }

    public async Task<string> SaveOriginalAsync(Stream videoStream, string extension, CancellationToken ct)
    {
        var uuidName = $"{Guid.NewGuid()}{extension}";
        var physicalPath = Path.Combine(_originalsFolder, uuidName);

        if (!Directory.Exists(_originalsFolder))
        {
            Directory.CreateDirectory(_originalsFolder);
        }

        await using var fileStream = new FileStream(physicalPath, FileMode.Create, FileAccess.Write, FileShare.None, 4096, useAsync: true);
        await videoStream.CopyToAsync(fileStream, ct);

        return physicalPath; // devuelve la ruta del archivo guardado
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
    public Task<Stream> GetFileStreamAsync(string filePath)
    {
        // Verificamos si el archivo existe antes de intentar abrirlo
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException("El archivo físico no existe en la ruta especificada.", filePath);
        }

        Stream stream = new FileStream(
            filePath,
            FileMode.Open,
            FileAccess.Read,
            FileShare.Read,
            bufferSize: 4096,
            useAsync: true);

        return Task.FromResult(stream);
    }

}