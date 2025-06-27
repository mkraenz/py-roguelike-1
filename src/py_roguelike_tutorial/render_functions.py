from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING

from py_roguelike_tutorial.colors import Theme

if TYPE_CHECKING:
    from tcod.console import Console
    from py_roguelike_tutorial.game_map import GameMap
    from py_roguelike_tutorial.engine import Engine


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
    entity_names = [
        entity.name
        for entity in game_map.visible_entities
        if entity.x == world_x and entity.y == world_y
    ]
    
    def count_names(acc: dict[str, int], name: str) -> dict[str, int]:
        if name in acc:
            acc[name] += 1
            return acc
        acc[name] = 1
        return acc

    names_with_count_dict = reduce(count_names, entity_names, {})

    def format_name(name: str, count: int) -> str:
        if count <= 1:
            return name
        return f"{count}x {name}"

    names_with_count = [
        format_name(name, count) for name, count in names_with_count_dict.items()
    ]

    names = ", ".join(names_with_count)
    return names.capitalize()


def render_names_at(
    console: Console, console_x: int, console_y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location
    names = get_entity_names_at(mouse_x, mouse_y, engine.game_map)
    console.print(
        x=console_x, y=console_y, text=names, fg=Theme.hover_over_entity_names
    )


YOU_DIED = '''M""MMMM""M MMP"""""YMM M""MMMMM""M M""""""'YMM M""M MM""""""""`M M""""""'YMM 
M. `MM' .M M' .mmm. `M M  MMMMM  M M  mmmm. `M M  M MM  mmmmmmmM M  mmmm. `M 
MM.    .MM M  MMMMM  M M  MMMMM  M M  MMMMM  M M  M M`      MMMM M  MMMMM  M 
MMMb  dMMM M  MMMMM  M M  MMMMM  M M  MMMMM  M M  M MM  MMMMMMMM M  MMMMM  M 
MMMM  MMMM M. `MMM' .M M  `MMM'  M M  MMMM' .M M  M MM  MMMMMMMM M  MMMM' .M 
MMMM  MMMM MMb     dMM Mb       dM M       .MM M  M MM        .M M       .MM 
MMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMM MMMM MMMMMMMMMMMM MMMMMMMMMMM 
'''


def render_you_died(console: Console):
    console.print(
        x=console.width // 2 - 76 // 2,
        y=console.height // 2 - 7 // 2 - 1,
        text=YOU_DIED,
        fg=Theme.you_died_text,
    )
