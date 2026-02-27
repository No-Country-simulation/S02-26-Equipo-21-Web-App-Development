using Microsoft.AspNetCore.Mvc;
using VideoShortsGenerator.Application.Services;
using System.Text.Json;

namespace VideoShortsGenerator.WebApi.Controllers;

[ApiController]
[Route("api/videos")]
public class VideosController : ControllerBase
{
    private readonly string[] _allowedExtensions = { ".mp4", ".mov", ".avi", ".mkv" };
    private readonly string[] _allowedMimeTypes = { "video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska" };
    private const long _maxFileSize = 150 * 1024 * 1024; // 150 MB
    private readonly VideoJobService _service;
    private readonly VideoJobQueryService _queryService;

    public VideosController(
        VideoJobService service,
        VideoJobQueryService queryService)
    {
        _service = service;
        _queryService = queryService;
    }

    // Ahora acepta un campo adicional 'paramsJson' en form-data (opcional)
    [HttpPost]
    public async Task<IActionResult> Create(IFormFile file, [FromForm(Name = "params")] string? paramsJson, CancellationToken ct)
    {
        // 1. Verificar si el archivo es nulo o está vacío
        if (file == null || file.Length == 0)
            return BadRequest("No se ha seleccionado ningún archivo.");

        // 2. Verificar el tamaño del archivo
        if (file.Length > _maxFileSize)
            return BadRequest("El archivo excede el límite de 150MB.");

        // 3. Verificar la extensión
        var extension = Path.GetExtension(file.FileName).ToLowerInvariant();
        if (string.IsNullOrEmpty(extension) || !_allowedExtensions.Contains(extension))
            return BadRequest("Extensión de archivo no permitida.");

        // 4. Verificar el tipo MIME (Content-Type)
        if (!_allowedMimeTypes.Contains(file.ContentType.ToLower()))
            return BadRequest("El tipo de contenido del archivo es inválido.");

        // Validar JSON de params si se proporcionó (no obligatorio)
        if (!string.IsNullOrWhiteSpace(paramsJson))
        {
            try
            {
                JsonDocument.Parse(paramsJson);
            }
            catch
            {
                return BadRequest("El campo 'params' debe ser un JSON válido.");
            }
        }

        var stream = file.OpenReadStream();
        // 5. Guardar el archivo y crear el job, pasando paramsJson
        var id = await _service.VideoUploadAsync(stream, file.FileName, paramsJson, ct);
        return CreatedAtAction(nameof(GetById), new { id }, new { Id = id });
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(Guid id)
    {
        var job = await _queryService.GetByIdAsync(id);

        if (job is null)
            return NotFound();

        return Ok(job);
    }

    [HttpGet("pending")]
    public async Task<IActionResult> GetPending()
    {
        var jobs = await _queryService.GetPendingAsync();
        return Ok(jobs);
    }

    [HttpGet("{id}/download")]
    public async Task<IActionResult> Download(Guid id, CancellationToken ct)
    {
        var (videoStream, fileName) = await _service.GetVideoDownloadAsync(id, ct);

        if (videoStream == null)
        {
            return NotFound("El video no está listo o no existe.");
        }

        return File(videoStream, "video/mp4", fileName);
    }
}