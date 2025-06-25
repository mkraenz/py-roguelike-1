from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.entity import Entity

player_prefab = Entity(char="@", color=Color.WHITE, name="Player", blocks_movement=True)

orc_prefab = Entity(char="o", color=Color.RED_ROBIN, name="Orc", blocks_movement=True)
troll_prefab = Entity(
    char="T", color=Color.DEEP_COOL_GREEN, name="Troll", blocks_movement=True
)
