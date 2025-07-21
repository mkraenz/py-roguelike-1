from typing import Final

from py_roguelike_tutorial.types import Coord


class Direction:
    N: Final[Coord] = (0, -1)
    S: Final[Coord] = (0, 1)
    W: Final[Coord] = (-1, 0)
    E: Final[Coord] = (1, 0)
    NW: Final[Coord] = (-1, -1)
    NE: Final[Coord] = (1, -1)
    SE: Final[Coord] = (1, 1)
    SW: Final[Coord] = (-1, 1)


INTERCARDINAL_DIRECTIONS = (
    Direction.N,
    Direction.S,
    Direction.W,
    Direction.E,
    Direction.NW,
    Direction.NE,
    Direction.SW,
    Direction.SE,
)

AUTOSAVE_FILENAME = "autosave.sav"
RNG_SEED = 98127391


from py_roguelike_tutorial.types import Rgb


def hex_to_rgb(hex_color: str) -> Rgb:
    if not hex_color.startswith("#"):
        raise AssertionError("hex_color must start with #")
    if not len(hex_color) == 7:
        raise AssertionError("hex_color must have 7 characters")
    return int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)


class Color:
    WHITE = hex_to_rgb("#FFFFFF")
    BLACK = hex_to_rgb("#000000")
    GREEN_ORC = hex_to_rgb("#3f7f3f")
    GREEN_DEEP_COOL = hex_to_rgb("#008800")
    RED_GUARDMANS = hex_to_rgb("#bf0000")
    GREEN_DARK = hex_to_rgb("#006000")
    RED_DARK_SIENNA = hex_to_rgb("#401010")
    GREY_88 = hex_to_rgb("#e0e0e0")
    GREY = hex_to_rgb("#808080")
    PINK_YOUR = hex_to_rgb("#ffc0c0")
    RED_FIREBRICK1 = hex_to_rgb("#ff3030")
    ORANGE_VIBRANT_WARM = hex_to_rgb("#ffa030")
    AZURE_LIGHT_WASHED = hex_to_rgb("#20a0ff")
    YELLOW = hex_to_rgb("#ffff00")
    YELLOW_DARK = hex_to_rgb("#101000")
    YELLOW_LIGHT = hex_to_rgb("#ffff33")
    RED_CORAL = hex_to_rgb("#FF4040")
    GREEN = hex_to_rgb("#00ff00")
    GREEN_SCREAMING = hex_to_rgb("#3fff3f")
    BLUE = hex_to_rgb("#0000ff")
    VIOLET = hex_to_rgb("#8000FF")
    RED = hex_to_rgb("#ff0000")
    PINK_INSANITY = hex_to_rgb("#cf3fff")
    BLUE_BABY = hex_to_rgb("#3fffff")
    MAGENTA_LIGHT = hex_to_rgb("#9f3fff")
    BLUE_NAVY = hex_to_rgb("#000064")
    BLUE_NAVY_DARK = hex_to_rgb("#000032")
    BLUE_LOCHMARA = hex_to_rgb("#323296")
    BLUE_DARK = hex_to_rgb("#08081f")
    YELLOW_AUTUMN_GOLD = hex_to_rgb("#c8b432")
    YELLOW_PALE_BROWN = hex_to_rgb("#826e32")


class Theme:
    player_attacks = Color.GREY_88
    enemy_attacks = Color.PINK_YOUR
    player_dies = Color.RED_FIREBRICK1
    enemy_dies = Color.ORANGE_VIBRANT_WARM
    welcome_text = Color.AZURE_LIGHT_WASHED
    hp_bar_text = Color.WHITE
    hp_bar_filled = Color.GREEN_DEEP_COOL
    hp_bar_empty = Color.RED_DARK_SIENNA
    you_died_text = Color.RED_FIREBRICK1
    log_message = Color.WHITE
    hover_over_entity_names = Color.WHITE
    invalid = Color.YELLOW
    impossible = Color.GREY
    error = Color.RED_CORAL
    health_recovered = Color.GREEN
    needs_target = Color.BLUE_BABY
    status_effect_applied = Color.GREEN_SCREAMING
    cursor_aoe = Color.RED
    menu_title = Color.YELLOW_LIGHT
    menu_text = Color.WHITE
    menu_background = Color.BLACK
    descend = Color.MAGENTA_LIGHT
