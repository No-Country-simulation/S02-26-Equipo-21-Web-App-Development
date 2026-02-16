using System;

namespace VideoShortsGenerator.Domain.Events;

public class VideoFailedEvent : IDomainEvent
{
    public Guid VideoId { get; }
    public DateTime OccurredOn { get; }

    public VideoFailedEvent(Guid videoId)
    {
        VideoId = videoId;
        OccurredOn = DateTime.UtcNow;
    }
}
