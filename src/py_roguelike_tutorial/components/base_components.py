from __future__ import annotations

from typing import TYPE_CHECKING

from py_roguelike_tutorial.colors import Theme

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Entity
    from py_roguelike_tutorial.game_map import GameMap
    from py_roguelike_tutorial.types import Rgb


class BaseComponent:
    """The entity owning the component"""

    parent: Entity

    @property
    def game_map(self) -> GameMap:
        return self.parent.game_map

    @property
    def engine(self) -> Engine:
        return self.parent.parent.engine

    def log(self, text: str, fg: Rgb = Theme.log_message):
        self.engine.message_log.add(text, fg)
