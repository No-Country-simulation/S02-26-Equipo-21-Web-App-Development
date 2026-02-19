namespace VideoShortsGenerator.Application.DTOs;

public sealed class VideoJobListResponse
{
    public Guid Id { get; set; }
    public string Status { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
}