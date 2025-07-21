from py_roguelike_tutorial.events.events import EventCallback, EventType, GameEvent


class EventBus:
    """An engine-wide event bus for managing game events."""

    def __init__(self):
        self._subscribers: dict[EventType, list[EventCallback]] = {}

    def subscribe(self, event_type: EventType, callback: EventCallback):
        """Subscribe a callback to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: EventCallback):
        """Unsubscribe a callback from a specific event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

    def unsubscribe_all(self):
        self._subscribers.clear()

    def publish(self, data: GameEvent):
        """Publish an event to all subscribers of the event type."""
        event_type = data["type"]
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(data)
