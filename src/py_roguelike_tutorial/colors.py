from py_roguelike_tutorial.types import Rgb


def hex_to_rgb(hex_color: str) -> Rgb:
    if not hex_color.startswith("#"):
        raise AssertionError("hex_color must start with #")
    if not len(hex_color) == 7:
        raise AssertionError("hex_color must have 7 characters")
    return int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED_ROBIN = (63, 127, 63)
    GREEN_DEEP_COOL = (0, 127, 0)
    RED_GUARDMANS = (191, 0, 0)
    GREEN = (0x0, 0x60, 0x0)
    RED_DARK_SIENNA = (0x40, 0x10, 0x10)
    GREY_88 = (0xE0, 0xE0, 0xE0)
    GREY = (0x80, 0x80, 0x80)
    PINK_YOUR = (0xFF, 0xC0, 0xC0)
    RED_FIREBRICK1 = (0xFF, 0x30, 0x30)
    ORANGE_VIBRANT_WARM = (0xFF, 0xA0, 0x30)
    AZURE_LIGHT_WASHED = (0x20, 0xA0, 0xFF)
    YELLOW = (0xFF, 0xFF, 0x00)
    YELLOW_LIGHT = hex_to_rgb("#ffff33")
    RED_CORAL = (0xFF, 0x40, 0x40)
    GREEN = (0x00, 0xFF, 0x00)
    GREEN_SCREAMING = hex_to_rgb("#3fff3f")
    BLUE = hex_to_rgb("#0000ff")
    VIOLET = (0x80, 0x00, 0xFF)
    RED = hex_to_rgb("#ff00ff")
    PINK_INSANITY = hex_to_rgb("#cf3fff")
    BLUE_BABY = hex_to_rgb("#3fffff")


class Theme:
    player_attacks = Color.GREY_88
    enemy_attacks = Color.PINK_YOUR
    player_dies = Color.RED_FIREBRICK1
    enemy_dies = Color.ORANGE_VIBRANT_WARM
    welcome_text = Color.AZURE_LIGHT_WASHED
    hp_bar_text = Color.WHITE
    hp_bar_filled = Color.GREEN
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


if __name__ == "__main__":
    print(Theme.status_effect_applied)
