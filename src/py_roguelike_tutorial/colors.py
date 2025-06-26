class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED_ROBIN = (63, 127, 63)
    GREEN_DEEP_COOL = (0, 127, 0)
    RED_GUARDMANS = (191, 0, 0)
    GREEN = (0x0, 0x60, 0x0)
    RED_DARK_SIENNA = (0x40, 0x10, 0x10)
    GREY_88 = (0xE0, 0xE0, 0xE0)
    PINK_YOUR = (0xFF, 0xC0, 0xC0)
    RED_FIREBRICK1 = (0xFF, 0x30, 0x30)
    ORANGE_VIBRANT_WARM = (0xFF, 0xA0, 0x30)
    AZURE_LIGHT_WASHED = (0x20, 0xA0, 0xFF)


class Theme:
    player_attacks = Color.GREY_88
    enemy_attacks = Color.PINK_YOUR
    player_dies = Color.RED_FIREBRICK1
    enemy_dies = Color.ORANGE_VIBRANT_WARM
    # GUI
    welcome_text = Color.AZURE_LIGHT_WASHED
    hp_bar_text = Color.WHITE
    hp_bar_filled = Color.GREEN
    hp_bar_empty = Color.RED_DARK_SIENNA
    you_died_text = Color.RED_FIREBRICK1
    log_message = Color.WHITE
    hover_over_entity_names = Color.WHITE
