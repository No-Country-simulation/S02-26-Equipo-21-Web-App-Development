using Microsoft.AspNetCore.Mvc;
using VideoShortsGenerator.Application.DTOs;
using VideoShortsGenerator.Application.Services;

namespace VideoShortsGenerator.WebApi.Controllers;

[ApiController]
[Route("api/videos")]
public class VideosController : ControllerBase
{
    private readonly VideoJobService _service;
    private readonly VideoJobQueryService _queryService;

    public VideosController(
        VideoJobService service,
        VideoJobQueryService queryService)
    {
        _service = service;
        _queryService = queryService;
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] CreateVideoJobRequest request)
    {
        try
        {
            var jobId = await _service.CreateAsync(request);
            return Ok(new { jobId });
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
        catch (FileNotFoundException ex)
        {
            return NotFound(new { error = ex.Message });
        }
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
}