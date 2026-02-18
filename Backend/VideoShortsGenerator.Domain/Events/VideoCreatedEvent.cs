namespace VideoShortsGenerator.Domain.Events;

public sealed class VideoCreatedEvent : IDomainEvent
{
    public Guid VideoId { get; }
    public DateTime OccurredOn { get; }

    public VideoCreatedEvent(Guid videoId)
    {
        VideoId = videoId;
        OccurredOn = DateTime.UtcNow;
    }
}
