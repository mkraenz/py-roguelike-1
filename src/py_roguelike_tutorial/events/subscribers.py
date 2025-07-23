from py_roguelike_tutorial.constants import Theme
from py_roguelike_tutorial.engine import Engine
import py_roguelike_tutorial.events.events as events
from py_roguelike_tutorial.handlers.dialogue_event_handler import DialogueEventHandler
from py_roguelike_tutorial.handlers.ranged_attack_animation import RangedAttackAnimation


class EventBusSubscribers:
    def __init__(self, engine: Engine):
        self.engine = engine

    def ranged_attack_animation(self):
        def callback(event: events.RangedAttackEvent) -> None:
            self.engine.stack.push(
                RangedAttackAnimation(
                    engine=self.engine,
                    from_pos=event.attacker_pos,
                    to=event.target_pos,
                    animation_tick_time_sec=0.05,
                )
            )

        self.engine.event_bus.subscribe(
            event_type=events.RangedAttackEvent, callback=callback
        )

    def talk(self):
        def callback(event: events.TalkEvent) -> None:
            self.engine.message_log.add(
                f'{event.target.name}: "Hi, would you like to buy something? We\'ve got the best prices."',
                fg=Theme.dialogue,
            )
            self.engine.stack.push(
                DialogueEventHandler(
                    engine=self.engine,
                    speaker=event.actor,
                    other=event.target,
                )
            )

        self.engine.event_bus.subscribe(event_type=events.TalkEvent, callback=callback)

    def add_subscribers(self):
        self.ranged_attack_animation()
        self.talk()
