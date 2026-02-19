using VideoShortsGenerator.Domain.Events;

namespace VideoShortsGenerator.Application.Abstractions;

public interface IEventDispatcher
{
    Task DispatchAsync(
        IEnumerable<IDomainEvent> events,
        CancellationToken cancellationToken = default);
}