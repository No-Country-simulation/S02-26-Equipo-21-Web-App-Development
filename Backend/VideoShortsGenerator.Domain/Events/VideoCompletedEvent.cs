using System;

namespace VideoShortsGenerator.Domain.Events;

public class VideoCompletedEvent : IDomainEvent
{
    public Guid VideoId { get; }
    public string OutputPath { get; }
    public DateTime OccurredOn { get; }

    public VideoCompletedEvent(Guid videoId, string outputPath)
    {
        VideoId = videoId;
        OutputPath = outputPath;
        OccurredOn = DateTime.UtcNow;
    }
}
