from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Entity


class BaseComponent:
    """The entity owning the component"""

    entity: Entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine
