from __future__ import annotations

from typing import TYPE_CHECKING

from py_roguelike_tutorial.entity import Entity

if TYPE_CHECKING:
    from py_roguelike_tutorial.behavior_trees.behavior_trees import Blackboard
    from py_roguelike_tutorial.entity import Actor


class VisualSense:
    agent: Actor

    def __init__(self, blackboard: Blackboard, interests: set[str], range: int):
        self.blackboard = blackboard
        self.interests = interests
        self.range = range

    @property
    def engine(self):
        return self.agent.parent.engine

    def sense(self):
        self.blackboard.clear_most()
        items = self.engine.game_map.items
        for item in items:
            common_tags = item.tags & self.interests
            if common_tags and self.can_see(item):
                for tag in common_tags:
                    self.blackboard.set(tag, item)

        for actor in self.engine.game_map.actors:
            common_tags = set(actor.tags) & self.interests
            if actor.is_alive and common_tags and self.can_see(actor):
                for tag in common_tags:
                    self.blackboard.set(tag, actor)

        if hasattr(self.agent, "inventory"):
            inventory_full = self.agent.inventory.is_full()
            self.blackboard.set("inventory_full", inventory_full)

    def can_see(self, other: Entity) -> bool:
        """Check if the agent can see the entity."""
        return self.agent.dist_chebyshev(
            other
        ) <= self.range and self.engine.game_map.has_line_of_sight(self.agent, other)
