from __future__ import annotations
from typing import TYPE_CHECKING

from py_roguelike_tutorial.colors import Theme

if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    from game_map import GameMap


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


def get_entity_names_at(world_x: int, world_y: int, game_map: GameMap) -> str:
    if (
        not game_map.in_bounds(world_x, world_y)
        or not game_map.visible[world_x, world_y]
    ):
        return ""
    names = ", ".join(
        entity.name
        for entity in game_map.visible_entities
        if entity.x == world_x and entity.y == world_y
    )
    return names.capitalize()


def render_names_at(
    console: Console, console_x: int, console_y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location
    names = get_entity_names_at(mouse_x, mouse_y, engine.game_map)
    console.print(
        x=console_x, y=console_y, text=names, fg=Theme.hover_over_entity_names
    )
