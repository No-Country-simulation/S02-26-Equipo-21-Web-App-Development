using VideoShortsGenerator.Application.Abstractions;
using VideoShortsGenerator.Application.EventHandlers;
using VideoShortsGenerator.Domain.Events;

namespace VideoShortsGenerator.Application.EventHandling;

public sealed class DomainEventDispatcher : IEventDispatcher
{
    private readonly VideoJobEventHandler _handler;

    public DomainEventDispatcher(VideoJobEventHandler handler)
    {
        _handler = handler;
    }

    public async Task DispatchAsync(
        IEnumerable<IDomainEvent> events,
        CancellationToken cancellationToken = default)
    {
        // Creamos una "instantánea" (snapshot) de los eventos actuales.
        // Esto desconecta la iteración de la lista original de la entidad.
        var eventsList = events.ToList();
        foreach (var domainEvent in eventsList)
        {
            switch (domainEvent)
            {
                case VideoCreatedEvent created:
                    await _handler.HandleAsync(created, cancellationToken);
                    break;

                case VideoProcessingStartedEvent started:
                    break;

                case VideoCompletedEvent completed:
                    await _handler.HandleAsync(completed, cancellationToken);
                    break;

                case VideoFailedEvent failed:
                    await _handler.HandleAsync(failed, cancellationToken);
                    break;
            }
        }
    }
}