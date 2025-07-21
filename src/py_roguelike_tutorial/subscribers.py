from py_roguelike_tutorial.engine import Engine
from py_roguelike_tutorial.handlers.ranged_attack_animation import RangedAttackAnimation


class EventBusSubscribers:
    def __init__(self, engine: Engine):
        self.engine = engine

    def ranged_attack_animation(self):
        def callback(event_type: str, data: dict) -> None:
            self.engine.stack.push(
                RangedAttackAnimation(
                    self.engine, data["attacker_pos"], data["target_pos"], 0.05
                )
            )

        self.engine.event_bus.subscribe(event_type="ranged_attack", callback=callback)

    def add_subscribers(self):
        self.ranged_attack_animation()
