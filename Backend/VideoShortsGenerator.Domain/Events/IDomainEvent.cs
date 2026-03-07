namespace VideoShortsGenerator.Domain.Events;

public interface IDomainEvent
{
    DateTime OccurredOn { get; }
}
