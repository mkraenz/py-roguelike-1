from __future__ import annotations

from typing import TYPE_CHECKING

from py_roguelike_tutorial.entity import Entity

if TYPE_CHECKING:
    from py_roguelike_tutorial.behavior_trees.behavior_trees import Blackboard
    from py_roguelike_tutorial.entity import Actor


class VisualSense:
    agent: Actor

    def __init__(self, blackboard: Blackboard, interests: list[str], range: int):
        self.blackboard = blackboard
        self.interests = interests
        self.range = range

    @property
    def engine(self):
        return self.agent.parent.engine

    def sense(self):
        items = self.engine.game_map.items
        for item in items:
            if item.kind in self.interests and self.can_see(item):
                self.blackboard.set(item.kind, item)
            else:
                self.blackboard.remove(item.kind)

        for actor in self.engine.game_map.actors:
            # TODO give npcs and players a 'category', 'archetype', 'type', or 'kind' attribute
            if actor.is_alive and actor.name in self.interests and self.can_see(actor):
                self.blackboard.set(actor.name, actor)
            else:
                self.blackboard.remove(actor.name)

        if hasattr(self.agent, "inventory"):
            inventory_full = self.agent.inventory.is_full()
            self.blackboard.set("inventory_full", inventory_full)

    def can_see(self, other: Entity) -> bool:
        """Check if the agent can see the entity."""
        return self.agent.dist_chebyshev(
            other
        ) <= self.range and self.engine.game_map.has_line_of_sight(self.agent, other)
