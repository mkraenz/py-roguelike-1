from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
from tcod.console import Console

from py_roguelike_tutorial.constants import Color
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine


class RangedAttackAnimation(IngameEventHandler):
    def __init__(
        self,
        engine: Engine,
        from_pos: Coord,
        to: Coord,
        animation_tick_time_sec: float = 0.1,
    ):
        super().__init__(engine)
        self.animation_tick_time_sec = animation_tick_time_sec
        self.elapsed: float = 0

        self.path = tcod.los.bresenham(from_pos, to)

    def on_render(self, console: Console, delta_time: float) -> None:

        super().on_render(console, delta_time)
        self.elapsed += delta_time
        ticks = int(self.elapsed / self.animation_tick_time_sec)
        if ticks >= len(self.path):
            self.engine.stack.pop()
            return
        pos = self.path[ticks] if ticks < len(self.path) else self.path[-1]
        child_console = Console(console.width, console.height)
        child_console.print(x=pos[0], y=pos[1], fg=Color.WHITE, text="x")
        child_console.blit(console, bg_alpha=0)

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        return None  # no key input while the animation is running for the time being. Maybe allow skipping
