from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
from tcod.console import Console

from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.render_functions import (
    print_aligned_texts_center,
    IngameMenuConsole,
)

if TYPE_CHECKING:
    pass


class CharacterSheetMenu(IngameEventHandler):
    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)  # draw main state as background
        child_console, blit = IngameMenuConsole(console, "Character Details")

        p = self.player
        texts = [
            f"Health:     {p.fighter.hp}/{p.fighter.max_hp} HP",
            "",
            "" f"Level:      {p.level.current_level}",
            f"Experience: {p.level.current_xp}/{p.level.xp_to_next_level} EXP",
            "",
            "" f"Strength:   {p.fighter.power}",
            f"Agility:    {p.fighter.defense}",
        ]

        print_aligned_texts_center(child_console, texts, console.height // 2 + -4)
        blit()

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        self.engine.stack.pop()
        return None
