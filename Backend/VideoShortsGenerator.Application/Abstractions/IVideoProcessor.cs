using VideoShortsGenerator.Domain.Enums;

namespace VideoShortsGenerator.Application.Abstractions;

public interface IVideoProcessor
{
    // Nueva firma: permite elegir venv/script y pasar parámetros JSON
    Task<Stream> ProcessAsync(
        string inputPath,
        ProcessingType processingType,
        string? paramsJson = null,
        CancellationToken cancellationToken = default);

    // Implementación por defecto para compatibilidad con código antiguo
    async Task<Stream> ProcessAsync(string inputPath, CancellationToken cancellationToken = default)
    {
        return await ProcessAsync(inputPath, ProcessingType.Simple, null, cancellationToken);
    }
}