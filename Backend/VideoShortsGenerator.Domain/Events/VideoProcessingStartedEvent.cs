namespace VideoShortsGenerator.Domain.Events;

public sealed class VideoProcessingStartedEvent : IDomainEvent
{
    public Guid VideoId { get; }
    public DateTime OccurredOn { get; }

    public VideoProcessingStartedEvent(Guid videoId)
    {
        VideoId = videoId;
        OccurredOn = DateTime.UtcNow;
    }
}
