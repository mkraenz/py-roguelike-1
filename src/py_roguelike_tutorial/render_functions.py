from __future__ import annotations
from typing import TYPE_CHECKING

from py_roguelike_tutorial.colors import Theme

if TYPE_CHECKING:
    from tcod.console import Console


def render_hp_bar(
    console: Console, current_value: int, max_value: int, total_width: int
) -> None:
    y = 45
    x = 0
    bar_width = int(float(current_value) / max_value * total_width)
    console.draw_rect(
        x=x, y=y, width=total_width, height=1, ch=1, bg=Theme.hp_bar_empty
    )
    if bar_width > 0:
        console.draw_rect(
            x=x, y=y, width=bar_width, height=1, ch=1, bg=Theme.hp_bar_filled
        )
    hp = f"HP: {current_value}/{max_value}"
    console.print(x=x + 1, y=y, text=hp, fg=Theme.hp_bar_text)
