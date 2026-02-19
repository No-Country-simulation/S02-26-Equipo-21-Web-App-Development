namespace VideoShortsGenerator.Application.DTOs;

public sealed class VideoJobResponse
{
    public Guid Id { get; set; }
    public string InputPath { get; set; } = string.Empty;
    public string? OutputPath { get; set; }
    public string Status { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
}