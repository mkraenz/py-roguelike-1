from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.constants import CENTER

from py_roguelike_tutorial.constants import Theme
from py_roguelike_tutorial.types import Rgb

if TYPE_CHECKING:
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
    hp = f"{current_value}/{max_value} HP"
    console.print(x=x + 1, y=y, text=hp, fg=Theme.hp_bar_text)


def _get_names_at(world_x: int, world_y: int, game_map: GameMap) -> str:
    if (
        not game_map.in_bounds(world_x, world_y)
        or not game_map.visible[world_x, world_y]
    ):
        return ""
    tile_name = game_map.tiles["name"][world_x, world_y]
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
    names_with_count_dict[tile_name] = 1

    def format_name(name: str, count: int) -> str:
        if count <= 1:
            return name
        return f"{count}x {name}"

    names_with_count = [
        format_name(name, count) for name, count in names_with_count_dict.items()
    ]

    names = ", ".join(names_with_count)
    return names.capitalize()


def render_names_at(console: Console, x: int, y: int, engine: Engine) -> None:
    mouse_x, mouse_y = engine.mouse_location
    names = f"({mouse_x},{mouse_y}) {_get_names_at(mouse_x, mouse_y, engine.game_map)}"
    console.print(x=x, y=y, text=names, fg=Theme.hover_over_entity_names)


_YOU_DIED = '''M""MMMM""M MMP"""""YMM M""MMMMM""M M""""""'YMM M""M MM""""""""`M M""""""'YMM 
M. `MM' .M M' .mmm. `M M  MMMMM  M M  mmmm. `M M  M MM  mmmmmmmM M  mmmm. `M 
MM.    .MM M  MMMMM  M M  MMMMM  M M  MMMMM  M M  M M`      MMMM M  MMMMM  M 
MMMb  dMMM M  MMMMM  M M  MMMMM  M M  MMMMM  M M  M MM  MMMMMMMM M  MMMMM  M 
MMMM  MMMM M. `MMM' .M M  `MMM'  M M  MMMM' .M M  M MM  MMMMMMMM M  MMMM' .M 
MMMM  MMMM MMb     dMM Mb       dM M       .MM M  M MM        .M M       .MM 
MMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMM MMMM MMMMMMMMMMMM MMMMMMMMMMM 
'''


def render_you_died(console: Console, x: int, y: int) -> None:
    console.print(
        x=x,
        y=y,
        width=console.width,
        text=_YOU_DIED,
        fg=Theme.you_died_text,
        alignment=CENTER,
    )


def render_dungeon_level(console: Console, dungeon_level: int, x: int, y: int) -> None:
    text = f"{dungeon_level}BF"
    console.print(
        x=x,
        y=y,
        text=text,
    )


def render_xp(
    console: Console, current_xp: int, xp_needed: int, x: int, y: int
) -> None:
    text = f"{current_xp} / {xp_needed} EXP"
    console.print(
        x=x,
        y=y,
        text=text,
    )


def dim_console(console: Console) -> None:
    console.rgb["fg"][:] //= 8
    console.rgb["bg"][:] //= 8


def print_text_center(
    console: Console,
    text: str,
    y: int,
    fg: Rgb = Theme.menu_text,
    bg: Rgb = Theme.menu_background,
    ljust_width: int = 0,
) -> None:
    justified = ljust_width == 0
    x = 0 if justified else console.width // 2
    txt = text if justified else text.ljust(ljust_width)
    width = console.width if justified else None
    console.print(x=x, y=y, text=txt, alignment=CENTER, fg=fg, bg=bg, width=width)


def print_text(
    console: Console,
    text: str,
    x: int,
    y: int,
    width: int,
    fg: Rgb = Theme.menu_text,
    bg: Rgb = Theme.menu_background,
) -> None:
    console.print(x=x, y=y, text=text, alignment=CENTER, fg=fg, bg=bg, width=width)


def print_aligned_texts_center(
    console: Console,
    lines: list[str],
    start_y: int,
):
    """Prints the given lines Left-aligned to the console."""
    width = max(map(len, lines))
    for i, text in enumerate(lines):
        y = start_y + i
        print_text_center(console, ljust_width=width, y=y, text=text)


def print_texts(
    console: Console,
    lines: list[str],
    *,
    x: int,
    start_y: int,
    width: int,
):
    for i, text in enumerate(lines):
        y = start_y + i
        print_text(console, x=x, y=y, text=text, width=width)


def render_border(console: Console) -> None:
    console.draw_frame(0, 0, console.width, console.height)


def IngameMenuConsole(console: Console, title: str):
    """Creates a child console with border and heading. Remember to `blit()` at the end of the calling method!"""
    child_console = Console(console.width - 6, console.height - 6)
    render_border(child_console)
    text = f"┤{title}├"
    print_text_center(child_console, text, 0)
    blit = lambda: child_console.blit(console, 3, 3)
    return child_console, blit
